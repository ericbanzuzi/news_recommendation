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

  public getSearchResponse(userId: string, query: string, daysBack: number, pageIdx: number): Observable<SearchResponse> {
    return this.http.get<SearchResponse>(`${this.apiServerUrl}/search?user_id=${userId}&query=${query}&days_back=${daysBack}&page=${pageIdx}`);
  }

  public provideFeedbackForArticle(user_id: string, article_id: string, action: string): Observable<boolean> {
    const userFeedback = {user_id: user_id, article_id: article_id, action: action};
    console.log(userFeedback);
    return this.http.post<boolean>(`${this.apiServerUrl}/provideFeedback`, userFeedback);
  }
}
