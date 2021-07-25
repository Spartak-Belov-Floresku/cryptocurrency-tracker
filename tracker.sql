--
-- PostgreSQL database dump
--

-- Dumped from database version 12.6 (Ubuntu 12.6-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.6 (Ubuntu 12.6-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE tracker;
--
-- Name: tracker; Type: DATABASE; Schema: -; Owner: -
--

CREATE DATABASE tracker WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'C.UTF-8' LC_CTYPE = 'C.UTF-8';


\connect tracker

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: apscheduler_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.apscheduler_jobs (
    id character varying(191) NOT NULL,
    next_run_time double precision,
    job_state bytea NOT NULL
);


--
-- Name: images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.images (
    user_id integer NOT NULL,
    image bytea NOT NULL
);


--
-- Name: providers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.providers (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    value character varying(30) NOT NULL
);


--
-- Name: providers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.providers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: providers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.providers_id_seq OWNED BY public.providers.id;


--
-- Name: recover_password; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recover_password (
    pin integer NOT NULL,
    username character varying(30) NOT NULL
);


--
-- Name: salts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.salts (
    user_id integer NOT NULL,
    value text NOT NULL
);


--
-- Name: tracking_coins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tracking_coins (
    id integer NOT NULL,
    user_id integer NOT NULL,
    coin_symbol character varying(10) NOT NULL,
    user_rate character varying(20) NOT NULL,
    by_email character varying(5) NOT NULL,
    by_phone character varying(5) NOT NULL,
    goes character varying(5) NOT NULL
);


--
-- Name: tracking_coins_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tracking_coins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tracking_coins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tracking_coins_id_seq OWNED BY public.tracking_coins.id;


--
-- Name: user_coins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_coins (
    id integer NOT NULL,
    user_id integer NOT NULL,
    coin_symbol character varying(10) NOT NULL
);


--
-- Name: user_coins_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_coins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_coins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_coins_id_seq OWNED BY public.user_coins.id;


--
-- Name: user_emails; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_emails (
    id integer NOT NULL,
    user_id integer NOT NULL,
    email character varying(120) NOT NULL,
    code_verified character varying(4),
    verified boolean NOT NULL
);


--
-- Name: user_emails_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_emails_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_emails_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_emails_id_seq OWNED BY public.user_emails.id;


--
-- Name: user_phone; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_phone (
    id integer NOT NULL,
    user_id integer NOT NULL,
    number character varying(10) NOT NULL,
    provider integer NOT NULL,
    code_verified character varying(4),
    verified boolean NOT NULL
);


--
-- Name: user_phone_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_phone_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_phone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_phone_id_seq OWNED BY public.user_phone.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(30) NOT NULL,
    full_name character varying(60) NOT NULL,
    password character varying(80) NOT NULL,
    public_id text NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: providers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.providers ALTER COLUMN id SET DEFAULT nextval('public.providers_id_seq'::regclass);


--
-- Name: tracking_coins id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracking_coins ALTER COLUMN id SET DEFAULT nextval('public.tracking_coins_id_seq'::regclass);


--
-- Name: user_coins id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_coins ALTER COLUMN id SET DEFAULT nextval('public.user_coins_id_seq'::regclass);


--
-- Name: user_emails id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_emails ALTER COLUMN id SET DEFAULT nextval('public.user_emails_id_seq'::regclass);


--
-- Name: user_phone id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_phone ALTER COLUMN id SET DEFAULT nextval('public.user_phone_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: apscheduler_jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.apscheduler_jobs (id, next_run_time, job_state) FROM stdin;
9eab4371e3ee48f3a0c9ef589c8c24f7	1626397085	\\x80059521040000000000007d94288c0776657273696f6e944b018c026964948c203965616234333731653365653438663361306339656635383963386332346637948c0466756e63948c106170703a73656e645f7265706f727473948c0774726967676572948c1961707363686564756c65722e74726967676572732e63726f6e948c0b43726f6e547269676765729493942981947d942868014b028c0874696d657a6f6e65948c047079747a948c025f70949394288c10416d65726963612f4e65775f596f726b944aa0baffff4b008c034c4d5494749452948c0a73746172745f64617465944e8c08656e645f64617465948c086461746574696d65948c086461746574696d65949394430a0807051e00000000000094680f2868104ab0b9ffff4b008c034553549474945294869452948c066669656c6473945d94288c2061707363686564756c65722e74726967676572732e63726f6e2e6669656c6473948c09426173654669656c649493942981947d94288c046e616d65948c0479656172948c0a69735f64656661756c7494888c0b65787072657373696f6e73945d948c2561707363686564756c65722e74726967676572732e63726f6e2e65787072657373696f6e73948c0d416c6c45787072657373696f6e9493942981947d948c0473746570944e736261756268218c0a4d6f6e74684669656c649493942981947d942868268c056d6f6e74689468288868295d94682d2981947d9468304e736261756268218c0f4461794f664d6f6e74684669656c649493942981947d942868268c036461799468288868295d94682d2981947d9468304e736261756268218c095765656b4669656c649493942981947d942868268c047765656b9468288868295d94682d2981947d9468304e736261756268218c0e4461794f665765656b4669656c649493942981947d942868268c0b6461795f6f665f7765656b9468288868295d94682d2981947d9468304e736261756268232981947d942868268c04686f75729468288868295d94682d2981947d9468304e736261756268232981947d942868268c066d696e7574659468288868295d94682d2981947d9468304e736261756268232981947d942868268c067365636f6e649468288968295d94682b8c0f52616e676545787072657373696f6e9493942981947d942868304e8c056669727374944b058c046c617374944b057562617562658c066a6974746572944e75628c086578656375746f72948c0764656661756c74948c046172677394298c066b7761726773947d9468268c0c73656e645f7265706f727473948c126d6973666972655f67726163655f74696d65944b018c08636f616c6573636594898c0d6d61785f696e7374616e636573944b038c0d6e6578745f72756e5f74696d65946818430a07e5070f143a0500000094680f2868104ac0c7ffff4d100e8c03454454947494529486945294752e
6845f5969f5f4fb0b2da3daaba758d4a	1626397085	\\x80059521040000000000007d94288c0776657273696f6e944b018c026964948c203638343566353936396635663466623062326461336461616261373538643461948c0466756e63948c106170703a73656e645f7265706f727473948c0774726967676572948c1961707363686564756c65722e74726967676572732e63726f6e948c0b43726f6e547269676765729493942981947d942868014b028c0874696d657a6f6e65948c047079747a948c025f70949394288c10416d65726963612f4e65775f596f726b944aa0baffff4b008c034c4d5494749452948c0a73746172745f64617465944e8c08656e645f64617465948c086461746574696d65948c086461746574696d65949394430a0807051e00000000000094680f2868104ab0b9ffff4b008c034553549474945294869452948c066669656c6473945d94288c2061707363686564756c65722e74726967676572732e63726f6e2e6669656c6473948c09426173654669656c649493942981947d94288c046e616d65948c0479656172948c0a69735f64656661756c7494888c0b65787072657373696f6e73945d948c2561707363686564756c65722e74726967676572732e63726f6e2e65787072657373696f6e73948c0d416c6c45787072657373696f6e9493942981947d948c0473746570944e736261756268218c0a4d6f6e74684669656c649493942981947d942868268c056d6f6e74689468288868295d94682d2981947d9468304e736261756268218c0f4461794f664d6f6e74684669656c649493942981947d942868268c036461799468288868295d94682d2981947d9468304e736261756268218c095765656b4669656c649493942981947d942868268c047765656b9468288868295d94682d2981947d9468304e736261756268218c0e4461794f665765656b4669656c649493942981947d942868268c0b6461795f6f665f7765656b9468288868295d94682d2981947d9468304e736261756268232981947d942868268c04686f75729468288868295d94682d2981947d9468304e736261756268232981947d942868268c066d696e7574659468288868295d94682d2981947d9468304e736261756268232981947d942868268c067365636f6e649468288968295d94682b8c0f52616e676545787072657373696f6e9493942981947d942868304e8c056669727374944b058c046c617374944b057562617562658c066a6974746572944e75628c086578656375746f72948c0764656661756c74948c046172677394298c066b7761726773947d9468268c0c73656e645f7265706f727473948c126d6973666972655f67726163655f74696d65944b018c08636f616c6573636594898c0d6d61785f696e7374616e636573944b038c0d6e6578745f72756e5f74696d65946818430a07e5070f143a0500000094680f2868104ac0c7ffff4d100e8c03454454947494529486945294752e
24bd9c8557f648bc8185e59d206507da	1626397085	\\x800595f9030000000000007d94288c0776657273696f6e944b018c026964948c203234626439633835353766363438626338313835653539643230363530376461948c0466756e63948c106170703a73656e645f7265706f727473948c0774726967676572948c1961707363686564756c65722e74726967676572732e63726f6e948c0b43726f6e547269676765729493942981947d942868014b028c0874696d657a6f6e65948c047079747a948c025f70949394288c10416d65726963612f4e65775f596f726b944aa0baffff4b008c034c4d5494749452948c0a73746172745f64617465944e8c08656e645f64617465944e8c066669656c6473945d94288c2061707363686564756c65722e74726967676572732e63726f6e2e6669656c6473948c09426173654669656c649493942981947d94288c046e616d65948c0479656172948c0a69735f64656661756c7494888c0b65787072657373696f6e73945d948c2561707363686564756c65722e74726967676572732e63726f6e2e65787072657373696f6e73948c0d416c6c45787072657373696f6e9493942981947d948c0473746570944e736261756268188c0a4d6f6e74684669656c649493942981947d9428681d8c056d6f6e746894681f8868205d9468242981947d9468274e736261756268188c0f4461794f664d6f6e74684669656c649493942981947d9428681d8c0364617994681f8868205d9468242981947d9468274e736261756268188c095765656b4669656c649493942981947d9428681d8c047765656b94681f8868205d9468242981947d9468274e736261756268188c0e4461794f665765656b4669656c649493942981947d9428681d8c0b6461795f6f665f7765656b94681f8868205d9468242981947d9468274e7362617562681a2981947d9428681d8c04686f757294681f8868205d9468242981947d9468274e7362617562681a2981947d9428681d8c066d696e75746594681f8868205d9468242981947d9468274e7362617562681a2981947d9428681d8c067365636f6e6494681f8968205d9468228c0f52616e676545787072657373696f6e9493942981947d942868274e8c056669727374944b058c046c617374944b057562617562658c066a6974746572944e75628c086578656375746f72948c0764656661756c74948c046172677394298c066b7761726773947d94681d8c0c73656e645f7265706f727473948c126d6973666972655f67726163655f74696d65944b018c08636f616c6573636594898c0d6d61785f696e7374616e636573944b038c0d6e6578745f72756e5f74696d65948c086461746574696d65948c086461746574696d65949394430a07e5070f143a0500000094680f2868104ac0c7ffff4d100e8c03454454947494529486945294752e
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.images (user_id, image) FROM stdin;
\.


--
-- Data for Name: providers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.providers (id, name, value) FROM stdin;
1	Verizon	@vtext.com
2	AT&T	@txt.att.net
3	Sprint	@messaging.sprintpcs.com
4	T-Mobile	@tmomail.net
5	U.S. Cellular	@email.uscc.net
\.


--
-- Data for Name: recover_password; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.recover_password (pin, username) FROM stdin;
\.


--
-- Data for Name: salts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.salts (user_id, value) FROM stdin;
\.


--
-- Data for Name: tracking_coins; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tracking_coins (id, user_id, coin_symbol, user_rate, by_email, by_phone, goes) FROM stdin;
\.


--
-- Data for Name: user_coins; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_coins (id, user_id, coin_symbol) FROM stdin;
\.


--
-- Data for Name: user_emails; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_emails (id, user_id, email, code_verified, verified) FROM stdin;
\.


--
-- Data for Name: user_phone; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_phone (id, user_id, number, provider, code_verified, verified) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, full_name, password, public_id) FROM stdin;
\.


--
-- Name: providers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.providers_id_seq', 5, true);


--
-- Name: tracking_coins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tracking_coins_id_seq', 1, false);


--
-- Name: user_coins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_coins_id_seq', 1, false);


--
-- Name: user_emails_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_emails_id_seq', 1, false);


--
-- Name: user_phone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_phone_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: apscheduler_jobs apscheduler_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apscheduler_jobs
    ADD CONSTRAINT apscheduler_jobs_pkey PRIMARY KEY (id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (user_id);


--
-- Name: providers providers_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_name_key UNIQUE (name);


--
-- Name: providers providers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_pkey PRIMARY KEY (id);


--
-- Name: recover_password recover_password_pin_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recover_password
    ADD CONSTRAINT recover_password_pin_key UNIQUE (pin);


--
-- Name: recover_password recover_password_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recover_password
    ADD CONSTRAINT recover_password_pkey PRIMARY KEY (pin, username);


--
-- Name: recover_password recover_password_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recover_password
    ADD CONSTRAINT recover_password_username_key UNIQUE (username);


--
-- Name: salts salts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salts
    ADD CONSTRAINT salts_pkey PRIMARY KEY (user_id);


--
-- Name: salts salts_value_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salts
    ADD CONSTRAINT salts_value_key UNIQUE (value);


--
-- Name: tracking_coins tracking_coins_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracking_coins
    ADD CONSTRAINT tracking_coins_id_key UNIQUE (id);


--
-- Name: tracking_coins tracking_coins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracking_coins
    ADD CONSTRAINT tracking_coins_pkey PRIMARY KEY (id, user_id, goes);


--
-- Name: user_coins user_coins_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_coins
    ADD CONSTRAINT user_coins_id_key UNIQUE (id);


--
-- Name: user_coins user_coins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_coins
    ADD CONSTRAINT user_coins_pkey PRIMARY KEY (id, user_id);


--
-- Name: user_emails user_emails_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_emails
    ADD CONSTRAINT user_emails_email_key UNIQUE (email);


--
-- Name: user_emails user_emails_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_emails
    ADD CONSTRAINT user_emails_id_key UNIQUE (id);


--
-- Name: user_emails user_emails_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_emails
    ADD CONSTRAINT user_emails_pkey PRIMARY KEY (id, user_id, email);


--
-- Name: user_emails user_emails_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_emails
    ADD CONSTRAINT user_emails_user_id_key UNIQUE (user_id);


--
-- Name: user_phone user_phone_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_phone
    ADD CONSTRAINT user_phone_id_key UNIQUE (id);


--
-- Name: user_phone user_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_phone
    ADD CONSTRAINT user_phone_number_key UNIQUE (number);


--
-- Name: user_phone user_phone_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_phone
    ADD CONSTRAINT user_phone_pkey PRIMARY KEY (id, user_id);


--
-- Name: user_phone user_phone_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_phone
    ADD CONSTRAINT user_phone_user_id_key UNIQUE (user_id);


--
-- Name: users users_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_key UNIQUE (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id, username, public_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ix_apscheduler_jobs_next_run_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_apscheduler_jobs_next_run_time ON public.apscheduler_jobs USING btree (next_run_time);


--
-- Name: images images_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: salts salts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salts
    ADD CONSTRAINT salts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: tracking_coins tracking_coins_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracking_coins
    ADD CONSTRAINT tracking_coins_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_coins user_coins_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_coins
    ADD CONSTRAINT user_coins_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_emails user_emails_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_emails
    ADD CONSTRAINT user_emails_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_phone user_phone_provider_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_phone
    ADD CONSTRAINT user_phone_provider_fkey FOREIGN KEY (provider) REFERENCES public.providers(id);


--
-- Name: user_phone user_phone_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_phone
    ADD CONSTRAINT user_phone_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

