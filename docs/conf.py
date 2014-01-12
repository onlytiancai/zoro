extensions = []

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'zoro'
copyright = u'2014, onlytiancai'

version = '0.1'
release = '0.1'
exclude_patterns = ['_build']

pygments_style = 'sphinx'
html_theme = 'default'
html_static_path = ['_static']
htmlhelp_basename = 'zorodoc'


latex_elements = {
}

latex_documents = [('index', 'zoro.tex', u'zoro Documentation',
                    u'onlytiancai', 'manual'),
                   ]

man_pages = [
    ('index', 'zoro', u'zoro Documentation',
     [u'onlytiancai'], 1)
]

texinfo_documents = [
    ('index', 'zoro', u'zoro Documentation',
     u'onlytiancai', 'zoro', 'One line description of project.',
     'Miscellaneous'),
]
