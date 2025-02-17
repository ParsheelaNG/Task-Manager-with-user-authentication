create database user;
use user;
create table signup(Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, Username varchar(100),Password varchar(300),MailID varchar(100),PhoneNumber varchar(100),Place varchar(100));
select * from signup;
create table tasks(Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,Taskname varchar(100),Taskdescription varchar(500),Deadline DATE,Priority varchar(20));
select * from tasks;
truncate table signup;
truncate table tasks;