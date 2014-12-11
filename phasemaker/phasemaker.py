# -*- coding: utf-8 -*-
import re
from mako.template import Template
from phasepersist import phasepersist
import settings

def get_post_filename(lang):
	if lang == 'es':
		return 'static/post-es.html'
	else:
		return 'static/post.html'

def get_index_filename(lang):
	if lang == 'es':
		return 'static/index-es.html'
	else:
		return 'static/index.html'

def get_uri(link, upper = False):
	add_relative = ''
	if upper:
		add_relative = '../'
	return add_relative + link.split('/')[-1:][0] + '.html'

def filename_from_tag(title):
	return title.replace(' ', '-').lower() + '.html'

def save_file(current_filename, page_content):
	new_file = open(current_filename, 'wb')
	new_file.write(page_content.encode('utf-8'))
	new_file.close()

def get_nav_footer(idx, posts):
	prev_url = prev_title = next_url = next_title = ''
	if idx == 0:
		next_url  = get_uri(posts[1]['link']) 
		next_title = posts[1]['title']
	elif idx < len(posts) - 1:
		prev_url = get_uri(posts[idx - 1]['link']) 
		prev_title = posts[idx - 1]['title']
		next_url = get_uri(posts[idx + 1]['link']) 
		next_title = posts[idx + 1]['title']
	elif idx == len(posts) - 1:
		prev_url = get_uri(posts[idx - 1]['link']) 
		prev_title = posts[idx - 1]['title']
	return (prev_url, prev_title, next_url, next_title)

def generate_posts(lang = 'en'):
	posts = phasepersist.load(lang)
	filename = get_post_filename(lang)
	canonical = Template(filename = filename)

	for idx, post in enumerate(posts):
		prev_url, prev_title, next_url, next_title = get_nav_footer(idx, posts)

		tag_tuples = [ ( filename_from_tag(tag) , tag) for tag in post['tags'] ]

		new_post = canonical.render(document_title = post['title'], 
			date = post['date'].strftime(settings.DATE_FORMAT),
			tags = tag_tuples,
			post_title = post['title'],
			post_description =  post['description'], 
			post_description_raw = re.sub('<[^>]*>', '',  post['description']),
			post_body = post['body'],
			next_url = next_url,
			next_title = next_title,
			prev_url = prev_url,
			prev_title = prev_title,
			settings.ANALYTICS_ID = settings.ANALYTICS_ID)
		new_name = get_uri(post['link'])
		save_file('output/' + new_name, new_post)	
		print new_name 

def get_nav_footer_index(idx, pages):
	newer = 'Recientes'
	older = 'Antiguas'
	prev_url = prev_title = next_url = next_title = ''
	cero = 'index.html'
	uno = 'index-#.html'
	if idx == 0 and len(pages) > 0:
		prev_url  = uno.replace('#','1') 
		prev_title =  older
	elif idx == 1 and len(pages) == 1:
		prev_url  = cero
		prev_title =  older
	elif idx == 1 and len(pages) > 1:
		prev_url = uno.replace('#','2') 
		prev_title = older
		next_url = cero
		next_title =  newer
	elif idx < len(pages) - 1:
		prev_url = uno.replace('#', str(idx+1)) 
		prev_title = older
		next_url  = uno.replace('#',str(idx-1)) 
		next_title =  newer
	elif idx == len(pages) - 1:
		next_url  = uno.replace('#',str(idx-1)) 
		next_title =  newer
	return (prev_url, prev_title, next_url, next_title)

def generate_blogindex(lang = 'en'):
	posts = phasepersist.load(lang)
	filename = get_index_filename(lang)
	canonical = Template(filename = filename)
	posts.reverse()
	pages = (len(posts) / settings.MAX_POST_PER_INDEX_PAGE) + 1
	for i in xrange(pages):
		start = settings.MAX_POST_PER_INDEX_PAGE * i 
		end = settings.MAX_POST_PER_INDEX_PAGE * (i + 1)
		if end > len(posts):
			end = len(posts)
		page_posts = posts[start:end]
		prev_url, prev_title, next_url, next_title = get_nav_footer_index(i, xrange(pages))

		elements = canonical.render(section_title = 'Blog',
			posts = page_posts,
			next_url = next_url,
			next_title = next_title,
			prev_url = prev_url,
			prev_title = prev_title,
			settings.ANALYTICS_ID = settings.ANALYTICS_ID,
			get_uri = get_uri,
			upper = False)

		if i == 0:
			new_name = 'index.html'
		else:
			new_name = 'index-%d.html' % i

		save_file('output/' + new_name, elements)
		print new_name 

def generate_tagindex(lang = 'en'):
	posts = phasepersist.load(lang)
	filename = get_index_filename(lang)
	canonical = Template(filename = filename)
	posts.reverse()

	tags = {}
	for post in posts:
		for tag in post['tags']:
			if tag in tags:
				tags[tag].append(post)
			else:
				tags[tag] = [post]

	for tag in tags.keys():
		tag_posts = tags[tag]
		prev_url = prev_title = next_url = next_title = ''
		elements = canonical.render(section_title = tag,
			posts = tag_posts,
			next_url = next_url,
			next_title = next_title,
			prev_url = prev_url,
			prev_title = prev_title,
			settings.ANALYTICS_ID = settings.ANALYTICS_ID,
			get_uri = get_uri,
			upper = True)

		new_name = filename_from_tag(tag)
		save_file('output/tags/' + new_name, elements)
		print new_name 

if __name__ == "__main__":
	lang = 'en'
	generate_posts(lang)
	generate_blogindex(lang)
	generate_tagindex(lang)