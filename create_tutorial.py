import markdown

tutorial = (markdown.markdown(open('tutorial.md').read()) +
   '</section>').replace('<h2>', '</section>\n<section>\n<h2>')

open('tutorial.html', 'w').write(tutorial)
