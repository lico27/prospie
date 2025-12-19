-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.area_hierarchy (
  parent_area_id character varying NOT NULL,
  child_area_id character varying NOT NULL,
  CONSTRAINT area_hierarchy_pkey PRIMARY KEY (parent_area_id, child_area_id),
  CONSTRAINT area_hierarchy_parent_area_id_fkey FOREIGN KEY (parent_area_id) REFERENCES public.areas(area_id),
  CONSTRAINT area_hierarchy_child_area_id_fkey FOREIGN KEY (child_area_id) REFERENCES public.areas(area_id)
);
CREATE TABLE public.areas (
  area_id character varying NOT NULL,
  area_level character varying NOT NULL,
  area_name character varying NOT NULL,
  CONSTRAINT areas_pkey PRIMARY KEY (area_id)
);
CREATE TABLE public.beneficiaries (
  ben_id character varying NOT NULL,
  ben_name character varying NOT NULL,
  CONSTRAINT beneficiaries_pkey PRIMARY KEY (ben_id)
);
CREATE TABLE public.causes (
  cause_id character varying NOT NULL,
  cause_name character varying NOT NULL,
  CONSTRAINT causes_pkey PRIMARY KEY (cause_id)
);
CREATE TABLE public.embedding_pairs (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  funder_registered_num character varying NOT NULL,
  recipient_id character varying NOT NULL,
  CONSTRAINT embedding_pairs_pkey PRIMARY KEY (id)
);
CREATE TABLE public.evaluation_pairs (
  id integer NOT NULL DEFAULT nextval('evaluation_pairs_id_seq'::regclass),
  funder_registered_num character varying NOT NULL,
  recipient_id character varying NOT NULL,
  CONSTRAINT evaluation_pairs_pkey PRIMARY KEY (id)
);
CREATE TABLE public.evaluation_responses (
  id integer NOT NULL DEFAULT nextval('evaluation_responses_id_seq'::regclass),
  pair_id integer,
  rating integer CHECK (rating >= 1 AND rating <= 100),
  CONSTRAINT evaluation_responses_pkey PRIMARY KEY (id),
  CONSTRAINT evaluation_responses_pair_id_fkey FOREIGN KEY (pair_id) REFERENCES public.evaluation_pairs(id)
);
CREATE TABLE public.financials (
  financials_id character varying NOT NULL,
  financials_year integer NOT NULL,
  financials_type character varying NOT NULL,
  financials_value numeric NOT NULL,
  CONSTRAINT financials_pkey PRIMARY KEY (financials_id)
);
CREATE TABLE public.funder_areas (
  registered_num character varying NOT NULL,
  area_id character varying NOT NULL,
  funder_areas_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  CONSTRAINT funder_areas_pkey PRIMARY KEY (area_id, funder_areas_id),
  CONSTRAINT funder_areas_registered_num_fkey FOREIGN KEY (registered_num) REFERENCES public.funders(registered_num),
  CONSTRAINT funder_areas_area_id_fkey FOREIGN KEY (area_id) REFERENCES public.areas(area_id)
);
CREATE TABLE public.funder_beneficiaries (
  registered_num character varying NOT NULL,
  ben_id character varying NOT NULL,
  funder_ben_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  CONSTRAINT funder_beneficiaries_pkey PRIMARY KEY (funder_ben_id),
  CONSTRAINT funder_beneficiaries_ben_id_fkey FOREIGN KEY (ben_id) REFERENCES public.beneficiaries(ben_id),
  CONSTRAINT funder_beneficiaries_registered_num_fkey FOREIGN KEY (registered_num) REFERENCES public.funders(registered_num)
);
CREATE TABLE public.funder_causes (
  registered_num character varying NOT NULL,
  cause_id character varying NOT NULL DEFAULT ''::character varying,
  funder_causes_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  CONSTRAINT funder_causes_pkey PRIMARY KEY (funder_causes_id),
  CONSTRAINT funder_causes_cause_id_fkey FOREIGN KEY (cause_id) REFERENCES public.causes(cause_id),
  CONSTRAINT funder_causes_registered_num_fkey FOREIGN KEY (registered_num) REFERENCES public.funders(registered_num)
);
CREATE TABLE public.funder_financials (
  funder_fin_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  registered_num character varying NOT NULL,
  financials_id character varying NOT NULL,
  CONSTRAINT funder_financials_pkey PRIMARY KEY (funder_fin_id),
  CONSTRAINT funder_financials_registered_num_fkey FOREIGN KEY (registered_num) REFERENCES public.funders(registered_num),
  CONSTRAINT funder_financials_financials_id_fkey FOREIGN KEY (financials_id) REFERENCES public.financials(financials_id)
);
CREATE TABLE public.funder_grants (
  registered_num character varying NOT NULL,
  funder_grants_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  grant_id character varying NOT NULL,
  CONSTRAINT funder_grants_pkey PRIMARY KEY (funder_grants_id),
  CONSTRAINT funder_grants_registered_num_fkey FOREIGN KEY (registered_num) REFERENCES public.funders(registered_num),
  CONSTRAINT funder_grants_grant_id_fkey FOREIGN KEY (grant_id) REFERENCES public.grants(grant_id)
);
CREATE TABLE public.funder_list (
  funder_list_id integer GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  registered_num character varying NOT NULL,
  list_id integer NOT NULL,
  CONSTRAINT funder_list_pkey PRIMARY KEY (funder_list_id),
  CONSTRAINT funder_list_registered_num_fkey FOREIGN KEY (registered_num) REFERENCES public.funders(registered_num),
  CONSTRAINT funder_list_list_id_fkey FOREIGN KEY (list_id) REFERENCES public.list_entries(list_id)
);
CREATE TABLE public.funders (
  registered_num character varying NOT NULL,
  name character varying NOT NULL,
  website character varying,
  activities text,
  objectives text,
  income_latest numeric,
  expenditure_latest numeric,
  objectives_activities text,
  achievements_performance text,
  grant_policy text,
  is_potential_sbf boolean NOT NULL DEFAULT false,
  is_on_list boolean NOT NULL DEFAULT false,
  is_nua boolean NOT NULL DEFAULT false,
  name_em USER-DEFINED,
  activities_em USER-DEFINED,
  objectives_em USER-DEFINED,
  objectives_activities_em USER-DEFINED,
  achievements_performance_em USER-DEFINED,
  grant_policy_em USER-DEFINED,
  concat_em USER-DEFINED,
  extracted_class text,
  CONSTRAINT funders_pkey PRIMARY KEY (registered_num)
);
CREATE TABLE public.grants (
  grant_title character varying,
  grant_desc text,
  amount numeric,
  year integer,
  grant_id character varying NOT NULL,
  source character varying,
  grant_title_em USER-DEFINED,
  grant_desc_em USER-DEFINED,
  grant_concat_em USER-DEFINED,
  grant_extracted_class text,
  CONSTRAINT grants_pkey PRIMARY KEY (grant_id)
);
CREATE TABLE public.list_entries (
  list_id integer GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  list_type character varying NOT NULL,
  list_date date NOT NULL,
  list_info text,
  CONSTRAINT list_entries_pkey PRIMARY KEY (list_id)
);
CREATE TABLE public.logic_pairs (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  funder_registered_num character varying NOT NULL,
  recipient_id character varying NOT NULL,
  CONSTRAINT logic_pairs_pkey PRIMARY KEY (id)
);
CREATE TABLE public.recipient_areas (
  recipient_areas_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  recipient_id character varying NOT NULL,
  area_id character varying NOT NULL,
  CONSTRAINT recipient_areas_pkey PRIMARY KEY (recipient_areas_id)
);
CREATE TABLE public.recipient_beneficiaries (
  recipient_ben_id integer GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  recipient_id character varying NOT NULL,
  ben_id character varying NOT NULL,
  CONSTRAINT recipient_beneficiaries_pkey PRIMARY KEY (recipient_ben_id),
  CONSTRAINT recipient_beneficiaries_ben_id_fkey FOREIGN KEY (ben_id) REFERENCES public.beneficiaries(ben_id),
  CONSTRAINT recipient_beneficiaries_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.recipients(recipient_id)
);
CREATE TABLE public.recipient_causes (
  recipient_cause_id integer GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  recipient_id character varying NOT NULL,
  cause_id character varying NOT NULL,
  CONSTRAINT recipient_causes_pkey PRIMARY KEY (recipient_cause_id),
  CONSTRAINT recipient_causes_cause_id_fkey FOREIGN KEY (cause_id) REFERENCES public.causes(cause_id),
  CONSTRAINT recipient_causes_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.recipients(recipient_id)
);
CREATE TABLE public.recipient_grants (
  recipient_id character varying NOT NULL,
  recipient_grants_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  grant_id character varying NOT NULL,
  CONSTRAINT recipient_grants_pkey PRIMARY KEY (recipient_grants_id),
  CONSTRAINT recipient_grants_grant_id_fkey FOREIGN KEY (grant_id) REFERENCES public.grants(grant_id),
  CONSTRAINT recipient_grants_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.recipients(recipient_id)
);
CREATE TABLE public.recipients (
  recipient_id character varying NOT NULL,
  recipient_name character varying NOT NULL,
  recipient_activities text,
  is_recipient boolean NOT NULL DEFAULT false,
  recipient_objectives text,
  recipient_name_em USER-DEFINED,
  recipient_activities_em USER-DEFINED,
  recipient_objectives_em USER-DEFINED,
  recipient_concat_em USER-DEFINED,
  recipient_extracted_class text,
  CONSTRAINT recipients_pkey PRIMARY KEY (recipient_id)
);