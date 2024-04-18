import {Component, OnInit} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {  HttpErrorResponse } from '@angular/common/http';
import { environment } from '../environments/environment';
import {ArticleService} from "./article.service";
import {NgFor} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {SearchResponse} from "./searchResponse";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet,NgFor,FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})


export class AppComponent implements OnInit {
  title = 'SearchEnginesUI';
  thumbsUpArticlesIdsSet = new Set();
  thumbsDownArticlesIdsSet = new Set();
  public searchResponse: SearchResponse | undefined;
  private apiServerUrl = environment.apiBaseUrl;
  AppComponent(){}
  ngOnInit() {
  }

  constructor(private articleService: ArticleService){}

  search(query: string, minPublishTimeStr: string) {
    let daysBack = -1;
    switch (minPublishTimeStr) {
      case "Last day":
        daysBack = 1;
        break;
      case "Last week":
        daysBack = 7;
        break;
      case "Last year":
        daysBack = 365;
    }
    this.articleService.getSearchResponse(query, daysBack).subscribe(
      (response: SearchResponse) => {
        for (let article of response.hits) {
          if (article.liked) {
            this.thumbsUpArticlesIdsSet.add(article.article_id);
          }
          if (article.disliked) {
            this.thumbsDownArticlesIdsSet.add(article.article_id);
          }
        }
        this.searchResponse = response;
      },
      (error: HttpErrorResponse) => {
        alert(error.message);
      }
    );
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
    if (this.thumbsUpArticlesIdsSet.has(article_id)) {
      this.thumbsUpArticlesIdsSet.delete(article_id);
    } else {
      this.thumbsDownArticlesIdsSet.delete(article_id);
      this.thumbsUpArticlesIdsSet.add(article_id);
    }
  }

  thumbsDownClick(article_id: string | undefined) {
    if (this.thumbsDownArticlesIdsSet.has(article_id)) {
      this.thumbsDownArticlesIdsSet.delete(article_id);
    } else {
      this.thumbsUpArticlesIdsSet.delete(article_id);
      this.thumbsDownArticlesIdsSet.add(article_id);
    }
  }


  protected readonly self = self;
}
