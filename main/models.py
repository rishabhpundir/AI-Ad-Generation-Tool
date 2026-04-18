from django.db import models

class TrafficSource(models.Model):
    """
    Represents traffic sources such as Facebook, Google, etc.
    """
    external_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class AdSource(models.Model):
    """
    Represents an advertising source linked to a platform (e.g., Facebook, Google).
    """
    ad_source_id = models.CharField(max_length=255, unique=True)
    ad_account_id = models.CharField(max_length=255)
    platform = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.platform} - {self.ad_source_id}"
    
class AdAccountAtrribution(models.Model):
    """
    Represents attribution ad accounts.
    """
    ad_source = models.ForeignKey(AdSource, on_delete=models.CASCADE, related_name="att_adsources")
    attribution_model = models.CharField(max_length=50, null=True, blank=True)
    attr_id = models.CharField(max_length=50, null=True, blank=True)
    clicks = models.CharField(max_length=50, null=True, blank=True) 
    cost = models.CharField(max_length=50, null=True, blank=True)
    cost_per_click = models.CharField(max_length=50, null=True, blank=True) 
    cost_per_lead = models.CharField(max_length=50, null=True, blank=True)
    cost_per_sale = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_unique_sales = models.CharField(max_length=50, null=True, blank=True)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ctr = models.CharField(max_length=50, null=True, blank=True)
    impressions = models.IntegerField(default=0, null=True, blank=True) 
    leads = models.IntegerField(default=0, null=True, blank=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    roas = models.IntegerField(default=0, null=True, blank=True)
    sales = models.IntegerField(default=0, null=True, blank=True)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unique_sales = models.IntegerField(default=0, null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.ad_source} - {self.attribution_model}"
    
class Source(models.Model):
    """
    Represents a campaign or marketing source.
    """
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255, unique=True)
    disregarded = models.BooleanField(default=False)
    organic = models.BooleanField(default=False)
    ad_source = models.ForeignKey(AdSource, on_delete=models.CASCADE, related_name="sources")
    traffic_source = models.ForeignKey(TrafficSource, on_delete=models.CASCADE, related_name="sources")
    creation_date = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.name

class Ad(models.Model):
    """
    Represents an individual ad within a Source.
    """
    name = models.CharField(max_length=255)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="ads")
    adsource = models.ForeignKey(AdSource, on_delete=models.SET_NULL, related_name="ad_adsrc", null=True, blank=True, default=None)
    adaccattr = models.ForeignKey(AdAccountAtrribution, on_delete=models.SET_NULL, related_name="ad_adattr", null=True, blank=True, default=None)
    creation_date = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.name

class Lead(models.Model):
    """
    Represents a lead generated from an advertisement.
    """
    email = models.EmailField(unique=True)
    external_id = models.CharField(max_length=255, unique=True)
    creation_date = models.CharField(null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    ips = models.JSONField(default=list, blank=True)  # Storing IPs as a list
    phone_numbers = models.JSONField(default=list, blank=True)  # Storing phone numbers as a list
    tags = models.JSONField(default=list, blank=True)  # Tags associated with the lead
    first_source = models.ForeignKey(Source, on_delete=models.SET_NULL, related_name="first_leads", null=True)
    last_source = models.ForeignKey(Source, on_delete=models.SET_NULL, related_name="last_leads", null=True)

    def __str__(self):
        return self.email
    
class Tag(models.Model):
    """
    Represents self-created tags.
    """
    tag = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.tag

