from django.db import models


class AdScript(models.Model):
    filename = models.CharField(max_length=255)
    ad_file = models.FileField(upload_to="adscripts/")
    platform = models.CharField(max_length=50, null=True, blank=True)
    ad_type = models.CharField(max_length=50, null=True, blank=True)
    industry = models.CharField(max_length=50, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} - {self.platform}"
