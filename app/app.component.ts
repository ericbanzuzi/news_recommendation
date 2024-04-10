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
  thumbsUpStatusClass = 'thumbs-up-no';
  thumbsDownStatusClass = 'thumbs-down-no';
  isThumbsUp = false;
  isThumbsDown = false;
  AppComponent(){}



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
