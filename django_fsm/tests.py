#!/usr/bin/env python
#-*- coding: utf-8 -*-

if __name__ == '__main__':
    from django import conf
    from django.core import management

    __name__ = 'django_fsm.tests'
    class TestSettings(conf.UserSettingsHolder):
        INSTALLED_APPS=('django_fsm',)
        DATABASE_ENGINE='sqlite3'

    conf.settings.configure(TestSettings(conf.global_settings))
    management.call_command('test', 'django_fsm')


from django.test import TestCase
from django.db import models
from django.contrib.contenttypes.models import ContentType

from django_fsm.db.fields import FSMField, transition

class BlogPost(models.Model):
    state = FSMField(default='new')

    @transition(source='new', target='published')
    def publish(self):
        pass

    @transition(source='published', target='hidden')
    def hide(self):
        pass

    @transition(source='new', target='removed')
    def remove(self):
        raise Exception('No rights to delete')


class FSMFieldTest(TestCase):
    def setUp(self):
        self.model = BlogPost()

    def test_initial_state_instatiated(self):
        self.assertEqual(self.model.state, 'new')

    def test_known_transition_should_succeed(self):
        self.model.publish()
        self.assertEqual(self.model.state, 'published')

        self.model.hide()
        self.assertEqual(self.model.state, 'hidden')

    def test_unknow_transition_fails(self):
        self.assertRaises(NotImplementedError, self.model.hide)

    def test_state_non_changed_after_fail(self):
        self.assertRaises(Exception, self.model.remove)
        self.assertEqual(self.model.state, 'new')


class InvalidModel(models.Model):
    state = FSMField(default='new')
    action = FSMField(default='no')

    @transition(source='new', target='no')
    def validate():
        pass


class InvalidModelTest(TestCase):
    def test_two_fsmfields_in_one_model_not_allowed(self):
        model = InvalidModel()
        self.assertRaises(TypeError, model.validate)


class Document(models.Model):
    status = FSMField(default='new')

    @transition(source='new', target='published')
    def publish(self):
        pass


class DocumentTest(TestCase):
    def test_any_state_field_name_allowed(self):
        model = Document()
        model.publish()
        self.assertEqual(model.status, 'published')

