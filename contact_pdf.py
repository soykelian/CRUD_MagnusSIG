from PIL import Image, ImageDraw
from pathlib import Path
files=sorted(Path('tmp/entrega4').glob('page-*.png'))
items=[]
for f in files:
    im=Image.open(f).convert('RGB')
    im.thumbnail((250,325))
    items.append((f.name,im.copy()))
out=Image.new('RGB',(5*270,((len(items)+4)//5)*355),'#dce3eb')
d=ImageDraw.Draw(out)
for i,(name,im) in enumerate(items):
    x=(i%5)*270+10; y=(i//5)*355+22
    out.paste(im,(x,y)); d.text((x,y-16),name,fill='#111111')
out.save('tmp/entrega4/contact.png')
