import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Article } from './article';
import { environment } from '../environments/environment';
import {SearchResponse} from "./searchResponse";
import {UserFeedback} from "./userFeedback";

@Injectable({providedIn: 'root'})
export class ArticleService {
  private apiServerUrl = environment.apiBaseUrl;

  constructor(private http: HttpClient){}

  public getSearchResponse(query: string, daysBack: number): Observable<SearchResponse> {
    return this.http.get<SearchResponse>(`${this.apiServerUrl}/search?user_id=erik&query=${query}&days_back=${daysBack}&page=0`);
  }

  public provideFeedbackForArticle(article_id: string, feedback: string): Observable<boolean> {
    const userFeedback = {user_id: 'erik', article_id: article_id, feedback: feedback};
    console.log(userFeedback);
    return this.http.post<boolean>(`${this.apiServerUrl}/provideFeedback`, userFeedback);
  }
}
