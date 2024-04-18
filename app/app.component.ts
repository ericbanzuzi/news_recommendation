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
  thumbsUpStatusClass = 'thumbs-up-no';
  thumbsDownStatusClass = 'thumbs-down-no';
  isThumbsUp = false;
  isThumbsDown = false;
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
        this.searchResponse = response;
        console.log(this.searchResponse?.hits);
      },
      (error: HttpErrorResponse) => {
        alert(error.message);
      }
    );
  }

  thumbsUpClick() {
    if (this.isThumbsUp) {
      this.isThumbsUp = false;
      this.thumbsUpStatusClass = 'thumbs-up-no';
      this.isThumbsDown = false;
      this.thumbsDownStatusClass = 'thumbs-down-no';
    } else {
      this.isThumbsUp = true;
      this.thumbsUpStatusClass = 'thumbs-up-yes';
      this.isThumbsDown = false;
      this.thumbsDownStatusClass = 'thumbs-down-no';
    }
  }

  thumbsDownClick() {
    if (this.isThumbsDown) {
      this.isThumbsDown = false;
      this.thumbsDownStatusClass = 'thumbs-down-no';
      this.isThumbsUp = false;
      this.thumbsUpStatusClass = 'thumbs-up-no';
    } else {
      this.isThumbsDown = true;
      this.thumbsDownStatusClass = 'thumbs-down-yes';
      this.isThumbsUp = false;
      this.thumbsUpStatusClass = 'thumbs-up-no';
    }
  }


  protected readonly self = self;
}
