BEGIN;

-- Updated seed: public.provide removed. Provider/cost/duration now live directly on public.training.

-- Clean reset for repeatable seed
TRUNCATE TABLE
    public.skill_validation,
    public.training_request,
    public.participation,
    public.trainingxskill,
    public.certificationxskill,
    public.diplomaxskill,
    public.employeexcertification,
    public.employeexdiploma,
    public.training,
    public.certification,
    public.diploma,
    public.training_source,
    public.validation_type,
    public.skill,
    public.employee,
    public.role,
    public.access_level,
    public.domaine
RESTART IDENTITY CASCADE;

-- Reference tables
INSERT INTO public.access_level (id_access_level, label, level) VALUES
(1, 'Employee', 1),
(2, 'Manager', 2),
(3, 'HR', 3);

INSERT INTO public.role (id_role, denomination_role, is_deleted, id_access_level) VALUES
(1, 'Admin RH', false, 3),
(2, 'Manager IT', false, 2),
(3, 'Developer', false, 1),
(4, 'Data Analyst', false, 1),
(5, 'Security Officer', false, 1),
(6, 'Project Manager', false, 2),
(7, 'Intern', false, 1);

INSERT INTO public.domaine (id_domaine, nom_domaine, is_deleted) VALUES
(1, 'Backend', false),
(2, 'Frontend', false),
(3, 'Database', false),
(4, 'DevOps', false),
(5, 'Security', false),
(6, 'Data', false),
(7, 'Project Management', false),
(8, 'Soft Skills', false);

INSERT INTO public.skill (id_skill, name_skill, is_deleted, id_domaine) VALUES
(1, 'Python', false,1),
(2, 'Java', false,1),
(3, 'SQL', false,3),
(4, 'PostgreSQL', false,3),
(5, 'SQLAlchemy', false,1),
(6, 'Alembic', false,1),
(7, 'Git', false,7),
(8, 'Docker', false,7),
(9, 'Linux', false,4),
(10, 'REST API', false,4),
(11, 'HTML/CSS', false,2),
(12, 'JavaScript', false,2),
(13, 'Cybersecurity Basics', false,5),
(14, 'Network Fundamentals', false,4),
(15, 'Data Analysis', false,1),
(16, 'Power BI', false,1),
(17, 'Agile Scrum', false,7),
(18, 'Communication', false,8),
(19, 'Testing', false,7),
(20, 'CI/CD', false,7);

INSERT INTO public.validation_type (id_validation, source, denomination_validation, is_deleted) VALUES
(1, 'manual', 'Manager validation', false),
(2, 'training', 'Training completion', false),
(3, 'certification', 'Certification obtained', false),
(4, 'diploma', 'Diploma obtained', false),
(5, 'self_assessment', 'Self assessment', false);

INSERT INTO public.training_source (id_source, name_source, is_deleted) VALUES
(1, 'Technifutur', false),
(2, 'Forem', false),
(3, 'OpenClassrooms', false),
(4, 'Udemy Business', false),
(5, 'ULiège', false),
(6, 'Odoo Academy', false),
(7, 'Internal HR', false);

-- Employees
-- Development password for every seeded employee: secret123 (Argon2 hash).
INSERT INTO public.employee (id_employee, first_name, last_name, hash_password, mail, is_deleted, id_role, id_manager) VALUES
(1, 'Alice', 'Lambert', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'alice.lambert@example.com', false, 1, NULL),
(2, 'Marc', 'Dubois', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'marc.dubois@example.com', false, 2, 1),
(3, 'Sophie', 'Renard', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'sophie.renard@example.com', false, 6, 1),
(4, 'David', 'Henrichmann', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'david.henrichmann@example.com', false, 3, 2),
(5, 'Nora', 'Simon', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'nora.simon@example.com', false, 3, 2),
(6, 'Thomas', 'Moreau', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'thomas.moreau@example.com', false, 3, 2),
(7, 'Elise', 'Laurent', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'elise.laurent@example.com', false, 4, 3),
(8, 'Karim', 'Benali', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'karim.benali@example.com', false, 4, 3),
(9, 'Julie', 'Petit', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'julie.petit@example.com', false, 5, 2),
(10, 'Hugo', 'Martin', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'hugo.martin@example.com', false, 7, 4),
(11, 'Emma', 'Leclercq', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'emma.leclercq@example.com', false, 7, 5),
(12, 'Louis', 'Fontaine', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'louis.fontaine@example.com', false, 3, 2),
(13, 'Maya', 'Bernard', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'maya.bernard@example.com', false, 5, 9),
(14, 'Noah', 'Dupont', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'noah.dupont@example.com', false, 4, 3),
(15, 'Claire', 'Rousseau', '$argon2id$v=19$m=65536,t=3,p=4$q8Kqg3cX/AEqALOBVou+Og$okCakO8e+kvXxzOzVLnt1mV13uPEfj98pyDg/6Dz/Wg', 'claire.rousseau@example.com', true, 3, 2);

-- Diplomas and certifications
INSERT INTO public.diploma (id_diploma, subject_diploma, level_diploma, is_deleted, id_domaine) VALUES
(1, 'Bachelier Informatique de Gestion', 'Bachelor', false, 1),
(2, 'Master Computer Science', 'Master', false, 1),
(3, 'Bachelier Réseaux et Télécoms', 'Bachelor', false, 4),
(4, 'Master Cybersecurity', 'Master', false, 5),
(5, 'Bachelier Data Science', 'Bachelor', false, 6),
(6, 'Gestion de projet informatique', 'Certificate Degree', false, 7);

INSERT INTO public.certification (id_certification, subject_certification, is_deleted, id_domaine) VALUES
(1, 'Python Professional', false, 1),
(2, 'Java Foundations', false, 1),
(3, 'PostgreSQL Associate', false, 3),
(4, 'Docker Fundamentals', false, 4),
(5, 'Linux Essentials', false, 4),
(6, 'Security Awareness', false, 5),
(7, 'Power BI Data Analyst', false, 6),
(8, 'Scrum Master I', false, 7),
(9, 'REST API Design', false, 1),
(10, 'Git Professional', false, 4);

-- Trainings
-- New model: a training may target either one certification OR one diploma OR only skills.
-- id_certification and id_diploma must not both be non-NULL.
INSERT INTO public.training (
    id_training,
    title,
    id_domaine,
    start_,
    end_,
    is_deleted,
    id_certification,
    id_diploma,
    id_source,
    cost_hour,
    duration_hours
) VALUES
(1, 'Python Backend Bootcamp', 1, '2026-01-08', '2026-01-19', false, 1, NULL, 1, 85.00, 70.00),
(2, 'Advanced SQL PostgreSQL', 3, '2026-02-05', '2026-02-09', false, 3, NULL, 1, 90.00, 35.00),
(3, 'SQLAlchemy and Alembic', 1, '2026-02-19', '2026-02-23', false, NULL, 1, 3, 55.00, 35.00),
(4, 'Docker for Developers', 4, '2026-03-04', '2026-03-06', false, 4, NULL, 4, 50.00, 21.00),
(5, 'Linux Administration Basics', 4, '2026-03-11', '2026-03-15', false, 5, NULL, 2, 70.00, 35.00),
(6, 'Security Awareness Workshop', 5, '2026-03-25', '2026-03-25', false, 6, NULL, 7, 0.00, 7.00),
(7, 'Power BI Reporting', 6, '2026-04-08', '2026-04-12', false, 7, NULL, 3, 60.00, 35.00),
(8, 'Agile Scrum Practice', 7, '2026-04-22', '2026-04-24', false, 8, NULL, 6, 95.00, 21.00),
(9, 'REST API Design', 1, '2026-05-06', '2026-05-10', false, 9, NULL, 1, 88.00, 35.00),
(10, 'Git Workflow Team Training', 4, '2026-05-20', '2026-05-21', false, 10, NULL, 7, 0.00, 14.00),
(11, 'Java Refresher', 1, '2026-06-03', '2026-06-07', false, 2, NULL, 4, 48.00, 35.00),
(12, 'Internal Communication', 8, '2026-06-17', '2026-06-17', false, NULL, NULL, 7, 0.00, 7.00),
(13, 'Bachelor IT Bridge Program', 1, '2026-07-06', '2026-07-31', false, NULL, 1, 5, 75.00, 120.00),
(14, 'Network Diploma Preparation', 4, '2026-08-03', '2026-08-21', false, NULL, 3, 2, 80.00, 105.00),
(15, 'Cybersecurity Master Preparation', 5, '2026-09-01', '2026-09-25', false, NULL, 4, 5, 120.00, 140.00),
(16, 'Data Science Diploma Track', 6, '2026-10-05', '2026-10-30', false, NULL, 5, 3, 90.00, 120.00),
(17, 'IT Project Management Degree Track', 7, '2026-11-02', '2026-11-20', false, NULL, 6, 6, 95.00, 90.00),
(18, 'SQLAlchemy Practice Workshop', 1, '2026-02-26', '2026-02-27', false, NULL, NULL, 7, 0.00, 14.00),
(19, 'Git and CI/CD Workshop', 7, '2026-05-25', '2026-05-26', false, NULL, NULL, 7, 0.00, 14.00),
(20, 'Testing Fundamentals Workshop', 7, '2026-06-10', '2026-06-11', false, NULL, NULL, 7, 0.00, 14.00);

-- Diploma requirements
INSERT INTO public.diplomaxskill (id_diploma, id_skill, min_level, is_deleted) VALUES
(1, 1, 3, false), (1, 2, 2, false), (1, 3, 3, false), (1, 7, 2, false),
(2, 1, 4, false), (2, 2, 4, false), (2, 10, 4, false), (2, 19, 3, false),
(3, 9, 3, false), (3, 14, 4, false), (3, 13, 2, false),
(4, 13, 5, false), (4, 14, 4, false), (4, 9, 3, false),
(5, 3, 4, false), (5, 15, 4, false), (5, 16, 3, false),
(6, 17, 4, false), (6, 18, 4, false);

-- Certification granted skills
INSERT INTO public.certificationxskill (id_certification, id_skill, granted_level, is_deleted) VALUES
(1, 1, 4, false), (1, 10, 3, false), (1, 19, 3, false),
(2, 2, 3, false), (2, 19, 2, false),
(3, 3, 4, false), (3, 4, 4, false),
(4, 8, 3, false), (4, 20, 2, false),
(5, 9, 3, false), (5, 14, 2, false),
(6, 13, 3, false), (6, 18, 2, false),
(7, 15, 4, false), (7, 16, 4, false),
(8, 17, 4, false), (8, 18, 3, false),
(9, 10, 4, false), (9, 1, 3, false),
(10, 7, 4, false), (10, 20, 2, false);

-- Training granted skills
-- Rule:
-- - If a training targets a certification, skills come from certificationxskill.
-- - If a training targets a diploma, skills come from diplomaxskill.
-- - Only skills-only trainings should appear here.
INSERT INTO public.trainingxskill (id_skill, id_training, granted_level, is_deleted) VALUES
(18, 12, 4, false),
(5, 18, 3, false),
(6, 18, 3, false),
(7, 19, 4, false),
(20, 19, 2, false),
(19, 20, 3, false);

-- Training -> diplomas/certifications are now stored directly in public.training

-- Employee diplomas
INSERT INTO public.employeexdiploma (id_employee, id_diploma, end_, school, start_, distinction, doc, is_deleted) VALUES
(4, 1, '2025-06-30', 'ECI Liège', '2021-09-15', 'Grande distinction', 'docs/diplomas/david_bachelor.pdf', false),
(5, 2, '2024-06-30', 'ULiège', '2019-09-15', 'Distinction', 'docs/diplomas/nora_master.pdf', false),
(6, 1, '2023-06-30', 'HEPL', '2020-09-15', NULL, 'docs/diplomas/thomas_bachelor.pdf', false),
(7, 5, '2022-06-30', 'HEC Liège', '2019-09-15', 'Distinction', 'docs/diplomas/elise_data.pdf', false),
(8, 5, '2021-06-30', 'ULB', '2018-09-15', NULL, 'docs/diplomas/karim_data.pdf', false),
(9, 4, '2020-06-30', 'UNamur', '2018-09-15', 'Grande distinction', 'docs/diplomas/julie_security.pdf', false),
(12, 1, '2024-06-30', 'ECI Liège', '2021-09-15', NULL, 'docs/diplomas/louis_bachelor.pdf', false),
(13, 4, '2025-06-30', 'ULiège', '2023-09-15', 'Distinction', 'docs/diplomas/maya_security.pdf', false),
(14, 5, '2023-06-30', 'HEC Liège', '2020-09-15', NULL, 'docs/diplomas/noah_data.pdf', false);

-- Employee certifications
INSERT INTO public.employeexcertification (id_employee_certification, id_employee, id_certification, start_, end_, expiration, organism, evaluation, doc, is_deleted) VALUES
(1, 4, 1, '2026-01-08', '2026-01-19', '2029-01-19', 'Technifutur', 'passed', 'docs/certifications/david_python.pdf', false),
(2, 4, 3, '2026-02-05', '2026-02-09', '2029-02-09', 'Technifutur', 'passed', 'docs/certifications/david_postgresql.pdf', false),
(3, 5, 1, '2025-09-01', '2025-09-15', '2028-09-15', 'OpenClassrooms', 'passed', 'docs/certifications/nora_python.pdf', false),
(4, 5, 9, '2025-11-10', '2025-11-14', '2028-11-14', 'Technifutur', 'passed', 'docs/certifications/nora_rest.pdf', false),
(5, 6, 2, '2026-06-03', '2026-06-07', '2029-06-07', 'Udemy Business', 'pending', NULL, false),
(6, 7, 7, '2026-04-08', '2026-04-12', '2029-04-12', 'OpenClassrooms', 'passed', 'docs/certifications/elise_powerbi.pdf', false),
(7, 8, 7, '2026-04-08', '2026-04-12', '2029-04-12', 'OpenClassrooms', 'failed', NULL, false),
(8, 9, 6, '2026-03-25', '2026-03-25', '2027-03-25', 'Internal HR', 'passed', 'docs/certifications/julie_security_awareness.pdf', false),
(9, 10, 10, '2026-05-20', '2026-05-21', '2029-05-21', 'Internal HR', 'passed', 'docs/certifications/hugo_git.pdf', false),
(10, 12, 4, '2026-03-04', '2026-03-06', '2029-03-06', 'Udemy Business', 'passed', 'docs/certifications/louis_docker.pdf', false),
(11, 13, 6, '2026-03-25', '2026-03-25', '2027-03-25', 'Internal HR', 'passed', 'docs/certifications/maya_security_awareness.pdf', false),
(12, 14, 7, '2026-04-08', '2026-04-12', '2029-04-12', 'OpenClassrooms', 'passed', 'docs/certifications/noah_powerbi.pdf', false);

-- Participations
INSERT INTO public.participation
(id_employee, id_training, status, is_deleted)
VALUES
(4, 1, 'COMPLETED', false),
(4, 2, 'COMPLETED', false),
(4, 3, 'COMPLETED', false),
(4, 18, 'COMPLETED', false),
(4, 19, 'COMPLETED', false),
(4, 20, 'COMPLETED', false),

(5, 1, 'COMPLETED', false),
(5, 9, 'COMPLETED', false),
(5, 10, 'REGISTERED', false),

(6, 2, 'COMPLETED', false),
(6, 4, 'REGISTERED', false),
(6, 11, 'IN_PROGRESS', false),

(7, 7, 'COMPLETED', false),
(7, 8, 'REGISTERED', false),

(8, 7, 'FAILED', false),
(8, 12, 'REGISTERED', false),

(9, 6, 'COMPLETED', false),
(9, 5, 'REGISTERED', false),

(10, 10, 'COMPLETED', false),

(11, 1, 'REGISTERED', false),
(11, 12, 'COMPLETED', false),

(12, 4, 'COMPLETED', false),
(12, 5, 'COMPLETED', false),
(12, 10, 'COMPLETED', false),

(13, 6, 'COMPLETED', false),

(14, 7, 'COMPLETED', false);

-- Training requests
INSERT INTO public.training_request
(
    id_training_request,
    status,
    reason,
    requested_at,
    is_deleted,
    id_employee,
    id_training,
    id_validator
)
VALUES
(1, 'VALIDATED', 'Backend onboarding', '2025-12-20', false, 4, 1, 2),
(2, 'VALIDATED', 'Need stronger SQL', '2026-01-15', false, 4, 2, 2),
(3, 'VALIDATED', 'ORM project need', '2026-01-30', false, 4, 3, 2),
(15, 'VALIDATED', 'Direct SQLAlchemy practice', '2026-02-24', false, 4, 18, 2),
(16, 'VALIDATED', 'Git and CI/CD upskilling', '2026-05-22', false, 4, 19, 2),
(17, 'VALIDATED', 'Testing fundamentals', '2026-06-08', false, 4, 20, 2),

(4, 'PENDING', 'API design improvement', '2026-05-01', false, 4, 9, NULL),

(5, 'VALIDATED', 'Team backend standard', '2025-12-22', false, 5, 1, 2),

(6, 'VALIDATED', 'Reporting needs', '2026-03-20', false, 7, 7, 3),

(7, 'REFUSED', 'Budget limit', '2026-03-21', false, 8, 7, 3),

(8, 'VALIDATED', 'Security compliance', '2026-03-01', false, 9, 6, 2),

(9, 'PENDING', 'Junior onboarding', '2026-05-25', false, 10, 1, NULL),

(10, 'VALIDATED', 'DevOps basics', '2026-02-20', false, 12, 4, 2),

(11, 'VALIDATED', 'Internal communication', '2026-06-01', false, 11, 12, 5),

(12, 'PENDING', 'Network basics', '2026-06-05', false, 13, 5, NULL),

(13, 'PENDING', 'SQL analysis', '2026-06-06', false, 14, 2, NULL),

(14, 'CANCELLED', 'Employee inactive', '2026-01-10', true, 15, 1, 2);

-- Skill validations
INSERT INTO public.skill_validation (id_skill_validation, date_, level_skill, id_validation, id_employee, id_validator, id_skill, is_deleted) VALUES
(1, '2026-01-20', 4, 3, 4, 2, 1, false),
(2, '2026-02-10', 4, 3, 4, 2, 3, false),
(3, '2026-02-10', 4, 3, 4, 2, 4, false),
(4, '2026-02-24', 3, 2, 4, 2, 5, false),
(5, '2026-02-24', 3, 2, 4, 2, 6, false),
(6, '2026-01-20', 3, 3, 5, 2, 1, false),
(7, '2025-11-15', 4, 3, 5, 2, 10, false),
(8, '2026-06-08', 3, 3, 6, 2, 2, false),
(9, '2026-04-13', 4, 3, 7, 3, 15, false),
(10, '2026-04-13', 4, 3, 7, 3, 16, false),
(11, '2026-04-13', 2, 2, 8, 3, 16, false),
(12, '2026-03-26', 3, 3, 9, 2, 13, false),
(13, '2026-05-22', 4, 2, 10, 4, 7, false),
(14, '2026-06-18', 4, 2, 11, 5, 18, false),
(15, '2026-03-07', 3, 3, 12, 2, 8, false),
(16, '2026-03-16', 3, 2, 12, 2, 9, false),
(17, '2026-03-26', 3, 3, 13, 9, 13, false),
(18, '2026-04-13', 4, 3, 14, 3, 15, false),
(19, '2026-04-13', 4, 3, 14, 3, 16, false),
(20, '2026-06-01', 2, 5, 10, 4, 1, false);

-- Make serial sequences consistent after explicit ids
SELECT setval(pg_get_serial_sequence('public.access_level', 'id_access_level'), COALESCE((SELECT MAX(id_access_level) FROM public.access_level), 1), true);
SELECT setval(pg_get_serial_sequence('public.role', 'id_role'), COALESCE((SELECT MAX(id_role) FROM public.role), 1), true);
SELECT setval(pg_get_serial_sequence('public.domaine', 'id_domaine'), COALESCE((SELECT MAX(id_domaine) FROM public.domaine), 1), true);
SELECT setval(pg_get_serial_sequence('public.skill', 'id_skill'), COALESCE((SELECT MAX(id_skill) FROM public.skill), 1), true);
SELECT setval(pg_get_serial_sequence('public.validation_type', 'id_validation'), COALESCE((SELECT MAX(id_validation) FROM public.validation_type), 1), true);
SELECT setval(pg_get_serial_sequence('public.training_source', 'id_source'), COALESCE((SELECT MAX(id_source) FROM public.training_source), 1), true);
SELECT setval(pg_get_serial_sequence('public.employee', 'id_employee'), COALESCE((SELECT MAX(id_employee) FROM public.employee), 1), true);
SELECT setval(pg_get_serial_sequence('public.diploma', 'id_diploma'), COALESCE((SELECT MAX(id_diploma) FROM public.diploma), 1), true);
SELECT setval(pg_get_serial_sequence('public.certification', 'id_certification'), COALESCE((SELECT MAX(id_certification) FROM public.certification), 1), true);
SELECT setval(pg_get_serial_sequence('public.training', 'id_training'), COALESCE((SELECT MAX(id_training) FROM public.training), 1), true);
SELECT setval(pg_get_serial_sequence('public.employeexcertification', 'id_employee_certification'), COALESCE((SELECT MAX(id_employee_certification) FROM public.employeexcertification), 1), true);
SELECT setval(pg_get_serial_sequence('public.training_request', 'id_training_request'), COALESCE((SELECT MAX(id_training_request) FROM public.training_request), 1), true);
SELECT setval(pg_get_serial_sequence('public.skill_validation', 'id_skill_validation'), COALESCE((SELECT MAX(id_skill_validation) FROM public.skill_validation), 1), true);

COMMIT;
