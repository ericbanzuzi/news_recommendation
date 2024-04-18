import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Article } from './article';
import { environment } from '../environments/environment';

@Injectable({providedIn: 'root'})
export class ArticleService {
  private apiServerUrl = environment.apiBaseUrl;

  constructor(private http: HttpClient){}

  public getArticles(query: string, daysBack: number): Observable<Article[]> {
    console.log(`${this.apiServerUrl}/search/?user_id=erik&query=${query}&min_publish_time=0&page=0`)
    return this.http.get<Article[]>(`${this.apiServerUrl}/search/?user_id=erik&query=${query}&days_back=${daysBack}&page=0`);
  }

  public provideFeedbackForArticle(article: Article): Observable<Article> {
    return this.http.post<Article>(`${this.apiServerUrl}/provideFeedback`, article);
  }
}
