use article_service;
select * from alembic_version;

select * from user;
select * from userlogins;
select * from articleversion;
select * from article;

update articleversion set articleId = null;
delete from article;
update articleversion set originalId = null;
delete from articleversion;
delete from userlogins;
delete from user;


ALTER TABLE article DROP CONSTRAINT article_ibfk_2;
DROP TABLE articleversion;
DROP TABLE article;
DROP TABLE userlogins;
DROP TABLE user;
DROP TABLE alembic_version;