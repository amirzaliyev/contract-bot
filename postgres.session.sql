-- select * from contracts;

insert into documents(file_name, owner_id, status, file_path, is_template) VALUES
('Mehnat shartnoma', 8131220463, 'public', 'static/contract_files/template2.docx', TRUE);
-- drop table contract_details;
-- drop table contracts;
-- drop table users;

-- drop table telegram_users;

-- select table_name from information_schema.tables where table_schema = 'public';

-- insert into template_fields(field_name, description, detail_order, contract_id)
-- values 
--     ('doc_number', 'Hujjat raqami', 1, 1),
--     ('fullname', 'Ishchining to''liq ismi', 2, 1);



-- select JSON_ARRAYAGG(contract_details) from contract_details;
-- alter table contract_details add column detail_order INT;
-- select * from contract_details;

-- select * from users;