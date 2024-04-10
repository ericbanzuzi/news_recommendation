import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'SearchEnginesUI';
  liked = 'Like';
  likeCount = 0;
  hasLiked = false;
  AppComponent(){}



  likeClick() {
    if (!this.hasLiked) {
      this.hasLiked = true;
      this.liked = 'Unlike';
      this.likeCount += 1;
    } else {
      this.hasLiked = false;
      this.liked = 'Like';
      this.likeCount -= 1;
    };
  }


  protected readonly self = self;
}
