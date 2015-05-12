
from django.template import Template, Context
from django.conf import settings
settings.configure()

t = Template('Hello {{ name }}')
c = Context({'name': 'Lyron'})

with open('test.txt',"w") as txt:
    txt.write(t.render(c))




