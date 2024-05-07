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

  public getSearchResponse(userId: string, query: string | String | null, daysBack: number | null, pageIdx: number): Observable<SearchResponse> {
    let url = `${this.apiServerUrl}/search?user_id=${userId}&page=${pageIdx}`
    if (query !== null) {
      url += `&query=${query}`;
    }
    if (daysBack !== null) {
      url += `&days_back=${daysBack}`;
    }
    return this.http.get<SearchResponse>(url);
  }

  public provideFeedbackForArticle(user_id: string, article_id: string, action: string): Observable<boolean> {
    const userFeedback = {user_id: user_id, article_id: article_id, action: action};
    console.log(userFeedback);
    return this.http.post<boolean>(`${this.apiServerUrl}/provideFeedback`, userFeedback);
  }
}
