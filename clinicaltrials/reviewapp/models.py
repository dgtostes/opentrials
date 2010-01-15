from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.conf import settings

from datetime import datetime

from registry.models import ClinicalTrial, Institution

from vocabulary.models import CountryCode

from utilities import safe_truncate

SUBMISSION_STATUS = [
    ('draft', 'draft'),
    ('pending', 'pending'),
    ('published', 'published'),
    ('rejected', 'rejected'),
]

class Submission(models.Model):
    creator = models.ForeignKey(User, related_name='submission_creator', editable=False)
    created = models.DateTimeField(default=datetime.now, editable=False)
    updater = models.ForeignKey(User, null=True, related_name='submission_updater', editable=False)
    updated = models.DateTimeField(null=True, editable=False)
    title = models.CharField(u'Scientific title', max_length=2000)
    primary_sponsor = models.OneToOneField(Institution, null=True, blank=True,
                                    verbose_name=_('Primary Sponsor'))

    trial = models.OneToOneField(ClinicalTrial, null=True)
    status = models.CharField(_('Status'), max_length=64,
                              choices=SUBMISSION_STATUS,
                              default=SUBMISSION_STATUS[0][0])
    staff_note = models.TextField(_('Submission Note (staff use only)'), max_length=255,
                                    blank=True)

    def save(self):
        if self.id:
            self.updated = datetime.now()
        super(Submission, self).save()

    def short_title(self):
        return safe_truncate(self.title, 120)

    def creator_username(self):
        return self.creator.username

    def __unicode__(self):
        return u'<%s> %s' % (self.creator_username(), self.short_title())

    def get_mandatory_languages(self):
        langs = set([u'EN'])
        langs.add(self.trial.primary_sponsor.country.language)
        
        for rc in self.trial.recruitmentcountry_set.all():
            langs.add(rc.country.language)
            
        return langs.intersection(settings.CHECKED_LANGUAGES)
        
    def get_absolute_url(self):
        return '/accounts/submission/%s/' % self.id
    
class RecruitmentCountry(models.Model):
    class Meta:
        verbose_name_plural = _('Recruitment Countries')    
    
    submission = models.ForeignKey(Submission)
    country = models.ForeignKey(CountryCode, verbose_name=_('Country'), related_name='submissionrecruitmentcountry_set')

    