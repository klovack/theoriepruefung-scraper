# Web scrape questions for Fahrprüfung

## What it does

- Crawl the website to get all questions for Theorieprüfung Klasse B

## Scrape

```sh
python scrape.py
```

What scrape does:

- go to the page
- **Go to Category Page:** For every element in `.teaser-list-chapters` navigate to the url in the `a` tag.
 ```html
<ul class="teaser-list-chapters">
	<li data-href="https://theoripruefung.de/fuer-fahrschueler/fuehrerschein-theorie-lernen/1-1/">
		<span class="id">Theorie Kapitel: 1.1</span>
		<a href="https://theoripruefung.de/fuer-fahrschueler/fuehrerschein-theorie-lernen/1-1/">
			Gefahrenlehre
		</a>
		<span class="count">
			<span class="label">Fragen</span>
			<span class="value">186</span>
		</span>
	</li>
	%% ... %%
</ul>
```
- **Get Question Category Text:**  In the opened page, find the question category by finding the `.question-headline`
Example 
```html
 <h1 class="question-headline">
  <span>Führerschein Theorie – Kapitel 1.1</span>
  Gefahrenlehre
 </h1>
```
- **Go to SubCategory Page:** For every element in another `.teaser-list-chapters` navigate to the url in the `a` tag
 ```html
 <ul class="teaser-list-chapters">
  <li data-href="https://theoripruefung.de/fuer-fahrschueler/fuehrerschein-theorie-lernen/1-1/1-1-01/">
	  <span class="id">Theorie Kapitel: 1.1.01</span>
	  <a href="https://theoripruefung.de/fuer-fahrschueler/fuehrerschein-theorie-lernen/1-1/1-1-01/">
		  Grundformen des Verkehrsverhaltens
	  </a>
	  <span class="count">
		  <span class="label">Fragen</span>
		  <span class="value">14</span>
	  </span>
  </li>
  %% ... %%
 </ul>
```
- **Get the SubCategory Text:** After navigating, find the question sub category by locating the `.queestion-headline`
 ```html
 <h1 class="question-headline">
  <span>Führerschein Theorie – Kapitel 1.1.01</span>
  Grundformen des Verkehrsverhaltens
 </h1>
```
- Getting the questions
- **Go to Question Page:** Find `.teaser-list-questions` and visit every link in `a` tag of its children by opening a new tab.
	```html
	<ul class="teaser-list-questions">
		<li data-href="https://theoripruefung.de/fuer-fahrschueler/fuehrerschein-theorie-lernen/1-1/1-1-01/1-1-01-001/">
			<img 
				decoding="async" 
				src="https://img.theoripruefung.de/fragenkatalog/default_image.jpg" 
				alt="1.1.01-001: Was versteht man unter defensivem Fahren?" 
				class="lazyloaded" 
				data-ll-status="loaded">
			<noscript>
				<img 
					decoding="async" 
					src="https://img.theoripruefung.de/fragenkatalog/default_image.jpg" 
					alt="1.1.01-001: Was versteht man unter defensivem Fahren?"/>
			</noscript>
			<a href="https://theoripruefung.de/fuer-fahrschueler/fuehrerschein-theorie-lernen/1-1/1-1-01/1-1-01-001/">
				<span class="id">Theorie Frage: 1.1.01-001</span>
				Was versteht man unter defensivem Fahren?
			</a>
		</li>
		%% ... %%
	</ul>
	```
- **Get the question:** Find div with `.question`
  ```html
  <div class="question">
	  <h1>Was versteht man unter defensivem Fahren? 
		  <span>Führerschein Theorie Frage:<br>1.1.01-001</span>
	  </h1>
	  <figure class="wp-block-video">
		  <video controls="" src="https://img.theoripruefung.de/fragenkatalog/2.1.01-007-M.mp4#t=0.1">
		  </video>
	  </figure>
	  <div class="image">
		  <img 
			  decoding="async" 
			  src="https://img.theoripruefung.de/fragenkatalog/1.2.06-101-M.jpg" 
			  alt="1.2.06-101-M: Wie verhalten Sie sich in dieser Situation richtig?" 
			  class="lazyloaded" 
			  data-ll-status="loaded">
			  <noscript>
				  <img 
					  decoding="async" 
					  src="https://img.theoripruefung.de/fragenkatalog/1.2.06-101-M.jpg" 
					  alt="1.2.06-101-M: Wie verhalten Sie sich in dieser Situation richtig?" />
			  </noscript>
			  <span class="caption">
			  </span>
	  </div>
	  <div class="body">
		  <div class="subtitle"></div>
		  <ul class="options">
			  <li data-result="true">
				  <span class="option-result true"></span>
				  <span class="option-box">Nicht auf dem eigenen Recht bestehen</span>
			  </li>
			  <li data-result="true">
				  <span class="option-result true"></span>
				  <span class="option-box">Mit Fehlern anderer rechnen</span>
			  </li>
			  <li data-result="false">
				  <span class="option-result false"></span>
				  <span class="option-box">Vorsorglich an jeder Kreuzung anhalten</span>
			  </li>
		  </ul>
		  <div class="points">Punkte: 4</div>
		  <div class="buttons">
			  <span class="cta-button cta-button__filled show-result">Lösung anzeigen</span>
			  <a 
				  href="https://theoripruefung.de/fuer-fahrschueler/fuehrerschein-theorie-lernen/1-1/1-1-01/1-1-01-002/" 
				  class="next cta-button cta-button__outlined">
					  Nächste Theoriefrage
			  </a>
		  </div>
		  <span class="disclaimer">
			  Offizielle TÜV | DEKRA Fragen für die Führerschein Theorieprüfung
		  </span>
	  </div>
  </div>
  ```
	- **Question Text:** Find an `h1` within a `div` with class `.question` but ignore everything that is in `span`
	- **(optional) Get the image:** Within the `div.question`, get the `src` attribute within an `img` tag
	- **(optional) Get the video:** Within the `div.question`, find `video` tag under `figure` tag and then grab the `src` attribute.
	- **Get sub question text:** Find a div with class `.subtitle` within `.question .body`.
	- **Get list of options:** For every `li` in `ul.options`, get the `innerText` of `span.option-box`
	- **Get the list of correct options:** For every `li` in `ul.options`, get the value of `data-result`. The index of correct options and options should be the same, therefore we can get it at the same time.
	- **Get the points:** Find `.points` within the `div.body` and  get its `innerText`. Split the text by space and get the second element in the array.
- Close the page, and go to the next question

## Translate

```sh
python translation.py
```

What it does:
- Get the questions from the disk that provided in the `config.py`
- Translate the questions by making the request to Deepl for getting the translation
