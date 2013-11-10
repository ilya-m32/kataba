import Image

def make_thumbnail(image,settings):
	ratio = min(settings.PIC_SIZE/image.height,settings.PIC_SIZE/image.width)
	thumbnail = Image.open(image.path)
	thumbnail.thumbnail((int(image.width*ratio),int(image.height*ratio)),Image.ANTIALIAS)
	thumbnail.save(settings.MEDIA_ROOT+'/thumbnails/'+image.name,thumbnail.format)
