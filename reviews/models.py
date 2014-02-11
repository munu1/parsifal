# coding: utf-8

import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    is_default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def set_url(self, value):
        if "http://" not in value and "https://" not in value and len(value) > 0:
            self.url = "http://" + str(value)
        else:
            self.url = value

    class Meta:
        verbose_name = "Source"
        verbose_name_plural = "Sources"
        ordering = ("name",)

class Review(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    author = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True, blank=True)
    last_update = models.DateTimeField()
    co_authors = models.ManyToManyField(User, related_name="co+")
    objective = models.TextField(max_length=1000, null=True, blank=True)
    sources = models.ManyToManyField(Source)

    def __unicode__(self):
        return self.name

    def save(self):
        self.last_update = datetime.datetime.now()
        super(Review, self).save()

    def get_questions(self):
        questions = Question.objects.filter(review__id=self.id)
        return questions

    def get_main_question(self):
        try:
            question = Question.objects.filter(review__id=self.id, question_type='M')[:1].get()
        except Question.DoesNotExist:
            question = Question()
        return question

    def get_secondary_questions(self):
        return Question.objects.filter(review__id=self.id, question_type='S')

    def get_inclusion_criterias(self):
        return SelectionCriteria.objects.filter(review__id=self.id, criteria_type='I')

    def get_exclusion_criterias(self):
        return SelectionCriteria.objects.filter(review__id=self.id, criteria_type='E')    

    def get_keywords(self):
        return Keyword.objects.filter(review__id=self.id, synonym_of=None)

    def is_author_or_coauthor(self, user):
        if user.id == self.author.id:
            return True
        for co_author in self.co_authors.all():
            if user.id == co_author.id:
                return True
        return False

    def get_generic_search_string(self):
        try:
            search_string = SearchSession.objects.filter(review__id=self.id, source=None)[:1].get()
        except SearchSession.DoesNotExist:
            search_string = SearchSession(review=self)
        return search_string

    def get_source_articles(self, source_id):
        return Article.objects.filter(review__id=self.id, source__id=source_id)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

class Question(models.Model):
    QUESTION_TYPES = (
            (u'M', u'Main'),
            (u'S', u'Secondary'),
        )
    review = models.ForeignKey(Review)
    question = models.CharField(max_length=500)
    population = models.CharField(max_length=200)
    intervention = models.CharField(max_length=200)
    comparison = models.CharField(max_length=200)
    outcome = models.CharField(max_length=200)
    question_type = models.CharField(max_length=1, choices=QUESTION_TYPES)

    def __unicode__(self):
        return self.question

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

class SelectionCriteria(models.Model):
    SELECTION_TYPES = (
            (u'I', u'Inclusion'),
            (u'E', u'Exclusion'),
        )

    review = models.ForeignKey(Review)
    criteria_type = models.CharField(max_length=1, choices=SELECTION_TYPES)
    description = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = "Selection Criteria"
        verbose_name_plural = "Selection Criterias"
        ordering = ("description",)

class SearchSession(models.Model):
    review = models.ForeignKey(Review)
    source = models.ForeignKey(Source, null=True)
    search_string = models.TextField(max_length=2000, null=True)

    def __unicode__(self):
        return self.search_string

class Article(models.Model):
    STATUS = (
            (u'U', u'Unclassified'),
            (u'R', u'Rejected'),
            (u'A', u'Accepted'),
        )
    review = models.ForeignKey(Review)
    bibtex_key = models.CharField(max_length=50)
    title = models.CharField(max_length=500, null=True)
    author = models.CharField(max_length=500, null=True)
    journal = models.CharField(max_length=500, null=True)
    year = models.CharField(max_length=4, null=True)
    source = models.ForeignKey(Source, null=True)
    pages = models.CharField(max_length=20, null=True)
    volume = models.CharField(max_length=20, null=True)
    author = models.CharField(max_length=500, null=True)
    abstract = models.TextField(max_length=4000, null=True)
    document_type = models.CharField(max_length=100, null=True)
    author_keywords = models.CharField(max_length=500, null=True)
    note = models.CharField(max_length=500, null=True)
    search_session = models.ForeignKey(SearchSession, null=True)
    status = models.CharField(max_length=1, choices=STATUS, default='U')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

class Keyword(models.Model):
    review = models.ForeignKey(Review)
    description = models.CharField(max_length=200)
    synonym_of = models.ForeignKey("self", null=True)
    
    def __unicode__(self):
        return self.description

    def get_synonyms(self):
        return Keyword.objects.filter(review__id=self.review.id, synonym_of__id=self.id)

    class Meta:
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"
        ordering = ("description",)