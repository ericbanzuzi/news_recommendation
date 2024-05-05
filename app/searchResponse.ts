import {Article} from "./article";

export interface SearchResponse {
  hits: Article[];
  num_results: number;
  delay_secs: number;
  spelling_suggestions: String[];
}
