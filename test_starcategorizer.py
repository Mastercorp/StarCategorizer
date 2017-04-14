import pytest
import StarCategorizer as sc


def test_load_file():
    assert sc.Model.load_file('testfile.txt') == 'this is a testfile\n'
    assert not sc.Model.load_file('not_here.txt')



def test_save_file():
    assert sc.Model.save_file('testfilesave.txt', 'testsave')
    assert not sc.Model.save_file('', 'test')



def test_backup_file():
    assert sc.Model.backup_file('testfile.txt')
    assert sc.Model.backup_file('testfile.txt')
    assert not sc.Model.backup_file('nofile.txt')


def test_find_begin_and_end_of_tag_and_level():
    tag_begin_curl, tag_end_curl, tag_level, tag_found = sc.Model.find_begin_and_end_of_tag_and_level(
        '\t\t\t\t"test"\n\t\t\t\t{\n\t\t\t\t}\n', 'test')
    assert tag_begin_curl == 1
    assert tag_end_curl == 2
    assert tag_level == 4
    assert tag_found


def test_delete_text_between_tags():
    assert sc.Model.delete_text_between_tags(
        '\t\t\t\t"test"\n\t\t\t\t{\nHier steht text\n\t\t\t\t}\n', 'test') == '\t\t\t\t"test"\n\t\t\t\t{\n\t\t\t\t}\n'
    assert sc.Model.delete_text_between_tags(
        '\t\t\t\t"test"\n\t\t\t\t{\n\t\t\t\t\t"0"\t\t"favorite"\n\t\t\t\t}\n', 'test') == \
        '\t\t\t\t"test"\n\t\t\t\t{\n\t\t\t\t\t"0"\t\t"favorite"\n\t\t\t\t}\n'
    assert sc.Model.delete_text_between_tags(
        '\n\n\n', 'test') == '\n\n\n'







