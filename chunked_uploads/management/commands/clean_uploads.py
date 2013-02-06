from django.core.management.base import BaseCommand
from django.conf import settings
from chunked_uploads.models import Upload
import datetime

class Command(BaseCommand):
    help = 'Clean failed and uncompleted uploads started 3 days ago or before'
    
    def handle(self, *args, **options):
        old = 3
       
        print("\nYou have request to delete all failed and uncompleted uploads\nstarted " + str(old) + " ago or before.")
        
        uncompleted_uploads = Upload.objects.filter(state=1)
        
        if len(uncompleted_uploads)==0:
            print ("\nNothing to delete")
        else:
            #tests if the uncompleted upload is more than 3 days old, if it is : deletes            
            for upload in uncompleted_uploads:
                if (datetime.datetime.now() - upload.created_at) > datetime.timedelta(days = old):
                    upload.delete()
            
            print ("\nDone")