INSERT INTO department (id, name, description) VALUES
('DPT-ADMN',   'Departamento de Administración', 'Descripción del Departamento de Administración'),
('DPT-HHRR', 'Departamento de Recursos Humanos', 'Descripción del Departamento de Recursos Humanos'),
('DPT-PROD',       'Departamento de Producción', 'Descripción del Departamento de Producción'),
('DPT-TEST',          'Departamento de Pruebas', 'Descripción del Departamento de Pruebas'),
('DPT-GSTS',        'Departamento de Invitados', 'Descripción del Departamento de Invitados');

INSERT INTO user (username, role, email, department_id, password) VALUES
(    'admin',     'admin', 'admin@lsoft.com', 'DPT-ADMN', 'scrypt:32768:8:1$kfLC1CP1Rk9oNnIE$1e1e255d3023562dd7a98a3368eba75a8e281cea2003e0188c8dc6df55cc296070763530ae732f97c47c486200bc734547238b27b3c323007e6d7a18f4d9945e'),
(  'manager',   'manager', 'mng_A@lsoft.com', 'DPT-PROD', 'scrypt:32768:8:1$bob4wge8Dbf7oJV9$d72286ee1075938cba6c6a2d905805e324fb2f5d8366af1d4224e9b4d3bb0530d5449c7319bece7b84e4f5bba56c35b3a8cd7730e9e326222749df84ee5127ac'),
('secretary', 'secretary', 'sct_B@lsoft.com', 'DPT-HHRR', 'scrypt:32768:8:1$nGiJFqnYRgXycdv6$f9f333e369e1771bb9244b603e41b81a199ce4e56605394b2b4e3d0895b9704c3c65aadab39b62cbe4ea10126a6371eef52c9b55bcf099a0089b235ffec6b470'),
(   'user01',      'user', 'usr_1@lsoft.com', 'DPT-TEST', 'scrypt:32768:8:1$a7skOl49RR3IvJoK$45b7c2158c0f5cb4e7b6fe525494de51893748211edf25fdbb85deb4b2597274af2c869698f28207bbb196cb8bfa2c1e19dbf61518bbe942e347052b189b92b9'),
(   'user02',      'user', 'usr_2@lsoft.com', 'DPT-PROD', 'scrypt:32768:8:1$YhD4ZiT0w4X3ftsd$337e75b3df55196ea9f2b03753448d96144f267802ab98b31af43992d324189f250d9158c1ecf0a041005f72243f8c209774e3b80725630951113dd141b9272b'),
(  'guest01',     'guest', 'gst_1@lsoft.com', 'DPT-GSTS', 'scrypt:32768:8:1$fDRNYwZhxTX9uIyw$07f7cad6b574f73967001cd5caad54eee6bd412d1d3d8f7c367300af20a5e12a1d16a3a82d412deadd5eb20d812adfe980aa7fd2d959d1539f84c36b53436d77'),
(  'guest02',     'guest', 'gst_2@lsoft.com', 'DPT-GSTS', 'scrypt:32768:8:1$4NUZ5DeHsQM29Qfs$030e0a832c59493d18b3825e4a790d7bad3c42b8e5e145df952e29bc15ece77ce346ebda7a4fefb73cf4629f2fafdf7b9e1a680b8d360a0341db27d2ea4db3f7');
