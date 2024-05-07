import {Component, OnInit} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {  HttpErrorResponse } from '@angular/common/http';
import { environment } from '../environments/environment';
import {ArticleService} from "./article.service";
import {Page} from "./page";
import {NgFor, NgIf} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {SearchResponse} from "./searchResponse";
import {min} from "rxjs";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet,NgFor,NgIf,FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})


export class AppComponent implements OnInit {
  minPublishTimeStr: string = 'Any time';
  userId: string | null = null;
  title = 'SearchEnginesUI';
  thumbsUpArticlesIdsSet = new Set();
  thumbsDownArticlesIdsSet = new Set();
  lastSearchQuery: string | String | null = null;
  lastSearchMinPublishTimeStr: string | null = null;
  searchResponse: SearchResponse | null = null;
  currentPageIdx: number | null = null;
  searchVal: string | String | null = '';
  spellingSuggestion: String  = '';
  wrongValue: string | String = '';
  private pageSize = environment.pageSize;
  private apiServerUrl = environment.apiBaseUrl;
  AppComponent(){}
  ngOnInit() {

  }

  constructor(private articleService: ArticleService){
    while (this.userId === null) {
      this.userId = prompt('Enter your username:');

    }
    this.search(null, 0);
  }

  setMinPublishTimeStr(minPublishTimeStr: string){
    this.minPublishTimeStr = minPublishTimeStr;
  }

  search(query: string | String | null, pageIdx: number) {
    if (this.userId === null) {
      return;
    }
    let daysBack: number | null = null;
    switch (this.minPublishTimeStr) {
      case "Last day":
        daysBack = 1;
        break;
      case "Last week":
        daysBack = 7;
        break;
      case "Last year":
        daysBack = 365;
    }
    this.articleService.getSearchResponse(this.userId, query, daysBack, pageIdx).subscribe(
      (response: SearchResponse) => {
        this.spellingSuggestion = '';
        this.wrongValue = '';
        this.lastSearchQuery = query;
        this.lastSearchMinPublishTimeStr = this.minPublishTimeStr;
        for (let article of response.hits) {
          if (article.liked) {
            this.thumbsUpArticlesIdsSet.add(article.article_id);
          }
          if (article.disliked) {
            this.thumbsDownArticlesIdsSet.add(article.article_id);
          }
        }
        this.searchResponse = response;
        this.currentPageIdx = pageIdx;
        if (query !== null && this.searchResponse.spelling_suggestions.length != 0){
          this.wrongValue = query;
          this.spellingSuggestion = this.searchResponse.spelling_suggestions[0];
        }
      },
      (error: HttpErrorResponse) => {
        alert(error.message);
      }
    );
  }

  searchFromSuggestions(query: string | String | null){
    this.search(query, 0)
    this.searchVal = String(query)
    this.spellingSuggestion = '';
    this.wrongValue = '';
    //this.searchResponse?.spelling_suggestions.
  }

  getThumbsUpStatusClass(article_id: string | undefined) {
    if (this.thumbsUpArticlesIdsSet.has(article_id)) {
      return 'thumbs-up-yes';
    }
    return 'thumbs-up-no';
  }

  getThumbsDownStatusClass(article_id: string | undefined) {
    if (this.thumbsDownArticlesIdsSet.has(article_id)) {
      return 'thumbs-down-yes';
    }
    return 'thumbs-down-no';
  }

  thumbsUpClick(article_id: string | undefined) {
    if (article_id && this.userId !== null) {
      if (this.thumbsUpArticlesIdsSet.has(article_id)) {
        this.articleService.provideFeedbackForArticle(this.userId, article_id, 'delete_like').subscribe(
          (response: boolean) => {
            this.thumbsUpArticlesIdsSet.delete(article_id);
          },
          (error: HttpErrorResponse) => {
            alert(error.message);
          }
        );
      } else {
        this.articleService.provideFeedbackForArticle(this.userId, article_id, 'add_like').subscribe(
          (response: boolean) => {
            this.thumbsDownArticlesIdsSet.delete(article_id);
            this.thumbsUpArticlesIdsSet.add(article_id);
          },
          (error: HttpErrorResponse) => {
            alert(error.message);
          }
        );
      }
    }
  }

  thumbsDownClick(article_id: string | undefined) {
    if (article_id && this.userId !== null) {
      if (this.thumbsDownArticlesIdsSet.has(article_id)) {
        this.articleService.provideFeedbackForArticle(this.userId, article_id, 'delete_dislike').subscribe(
          (response: boolean) => {
            this.thumbsDownArticlesIdsSet.delete(article_id);
          },
          (error: HttpErrorResponse) => {
            alert(error.message);
          }
        );
      } else {
        this.articleService.provideFeedbackForArticle(this.userId, article_id, 'add_dislike').subscribe(
          (response: boolean) => {
            this.thumbsUpArticlesIdsSet.delete(article_id);
            this.thumbsDownArticlesIdsSet.add(article_id);
          },
          (error: HttpErrorResponse) => {
            alert(error.message);
          }
        );
      }
    }
  }

  getSearchResultsCountText() {
    if (this.searchResponse) {
      return `About ${this.searchResponse?.num_results} (${this.searchResponse?.delay_secs?.toFixed(2)} seconds) results`;
    }
    else {
      return "";
    }
  }

  getPages() {
    const pages: Page[] = [];
    if (this.searchResponse !== null && this.currentPageIdx !== null) {
      const numAvailablePages = Math.ceil(this.searchResponse.num_results / this.pageSize);
      pages.push({
        text: 'Prev',
        isActive: false,
        isDisabled: (this.currentPageIdx == 0),
        pageIdx: this.currentPageIdx - 1
      });
      pages.push({
        text: '1',
        isActive: (this.currentPageIdx == 0),
        isDisabled: false,
        pageIdx: 0
      });
      if (Math.min(this.currentPageIdx + environment.currentPageRightWindow + 1, numAvailablePages) <= environment.maxPagesToDisplay) {
        for (let pageIdx = 1; pageIdx < Math.min(numAvailablePages, environment.maxPagesToDisplay); ++pageIdx) {
          pages.push({
            text: `${pageIdx + 1}`,
            isActive: (this.currentPageIdx == pageIdx),
            isDisabled: false,
            pageIdx: pageIdx
          });
        }
      }
      else {
        pages.push({
          text: '...',
          isActive: false,
          isDisabled: false,
          pageIdx: 1
        });
        const startPageIdxAfterDots = this.currentPageIdx + environment.currentPageRightWindow - environment.maxPagesToDisplay + 3;
        for (let pageIdx = startPageIdxAfterDots; pageIdx <= this.currentPageIdx + environment.currentPageRightWindow; ++pageIdx) {
          pages.push({
            text: `${pageIdx + 1}`,
            isActive: (this.currentPageIdx == pageIdx),
            isDisabled: false,
            pageIdx: pageIdx
          });
        }
      }
      pages.push({
        text: 'Next',
        isActive: false,
        isDisabled: (this.currentPageIdx == numAvailablePages - 1),
        pageIdx: this.currentPageIdx + 1
      });
    }
    return pages;
  }

  getPageClassString(page: Page) {
    const pageClassesStrings: string[] = [];
    if (page.isActive) {
      pageClassesStrings.push('active');
    }
    if (page.isDisabled) {
      pageClassesStrings.push('disabled');
    }
    return pageClassesStrings.join(' ');
  }

  protected readonly self = self;
}
