--
-- Create model Currency
--
CREATE TABLE `subscriptions_currency` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `code` varchar(3) NOT NULL UNIQUE, `symbol` varchar(5) NOT NULL, `decimals` smallint UNSIGNED NOT NULL CHECK (`decimals` >= 0), `last_updated` datetime(6) NULL);
--
-- Create model Provider
--
CREATE TABLE `subscriptions_provider` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(120) NOT NULL, `slug` varchar(50) NOT NULL UNIQUE, `website` varchar(200) NULL, `category` varchar(50) NOT NULL, `logo` varchar(100) NULL, `created_at` datetime(6) NOT NULL);
--
-- Create model AuditLog
--
CREATE TABLE `subscriptions_auditlog` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `action` varchar(20) NOT NULL, `model_name` varchar(200) NOT NULL, `object_pk` varchar(200) NULL, `changes` json NULL, `ip_address` char(39) NULL, `timestamp` datetime(6) NOT NULL, `user_id` integer NULL);
--
-- Create model PaymentMethod
--
CREATE TABLE `subscriptions_paymentmethod` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `kind` varchar(30) NOT NULL, `token` varchar(255) NOT NULL, `last4` varchar(4) NULL, `brand` varchar(50) NULL, `is_default` bool NOT NULL, `metadata` json NULL, `created_at` datetime(6) NOT NULL, `user_id` integer NOT NULL);
--
-- Create model Plan
--
CREATE TABLE `subscriptions_plan` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(120) NOT NULL, `duration_days` integer UNSIGNED NOT NULL CHECK (`duration_days` >= 0), `price` numeric(12, 2) NOT NULL, `description` longtext NOT NULL, `created_at` datetime(6) NOT NULL, `currency_id` bigint NOT NULL, `provider_id` bigint NOT NULL);
--
-- Create model Subscription
--
CREATE TABLE `subscriptions_subscription` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `start_date` datetime(6) NOT NULL, `end_date` datetime(6) NOT NULL, `auto_renew` bool NOT NULL, `status` varchar(20) NOT NULL, `description` longtext NULL, `external_id` varchar(255) NULL, `metadata` json NULL, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `currency_id` bigint NOT NULL, `plan_id` bigint NULL, `provider_id` bigint NOT NULL, `user_id` integer NOT NULL);
--
-- Create model Payment
--
CREATE TABLE `subscriptions_payment` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `amount` numeric(12, 2) NOT NULL, `exchange_rate` numeric(18, 8) NULL, `fee` numeric(12, 2) NOT NULL, `status` varchar(20) NOT NULL, `reference` varchar(255) NULL, `gateway_response` json NULL, `paid_at` datetime(6) NULL, `created_at` datetime(6) NOT NULL, `currency_id` bigint NOT NULL, `user_id` integer NOT NULL, `payment_method_id` bigint NULL, `subscription_id` bigint NULL);
--
-- Create model Notification
--
CREATE TABLE `subscriptions_notification` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `kind` varchar(50) NOT NULL, `send_at` datetime(6) NOT NULL, `sent_at` datetime(6) NULL, `payload` json NULL, `read` bool NOT NULL, `created_at` datetime(6) NOT NULL, `user_id` integer NOT NULL, `subscription_id` bigint NULL);
--
-- Create model Comment
--
CREATE TABLE `subscriptions_comment` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `metadata` json NULL, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` integer NOT NULL, `subscription_id` bigint NOT NULL);
--
-- Create index subscriptio_user_id_2a19e8_idx on field(s) user, status of model subscription
--
CREATE INDEX `subscriptio_user_id_2a19e8_idx` ON `subscriptions_subscription` (`user_id`, `status`);
--
-- Create index subscriptio_end_dat_60694b_idx on field(s) end_date of model subscription
--
CREATE INDEX `subscriptio_end_dat_60694b_idx` ON `subscriptions_subscription` (`end_date`);
--
-- Create index subscriptio_referen_5d56d6_idx on field(s) reference of model payment
--
CREATE INDEX `subscriptio_referen_5d56d6_idx` ON `subscriptions_payment` (`reference`);
--
-- Create index subscriptio_status_ee37b6_idx on field(s) status of model payment
--
CREATE INDEX `subscriptio_status_ee37b6_idx` ON `subscriptions_payment` (`status`);
--
-- Create index subscriptio_user_id_af0fbb_idx on field(s) user, send_at of model notification
--
CREATE INDEX `subscriptio_user_id_af0fbb_idx` ON `subscriptions_notification` (`user_id`, `send_at`);
--
-- Create index subscriptio_sent_at_c5e521_idx on field(s) sent_at of model notification
--
CREATE INDEX `subscriptio_sent_at_c5e521_idx` ON `subscriptions_notification` (`sent_at`);
ALTER TABLE `subscriptions_auditlog` ADD CONSTRAINT `subscriptions_auditlog_user_id_8b691405_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `subscriptions_paymentmethod` ADD CONSTRAINT `subscriptions_paymentmethod_user_id_52d5d00c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `subscriptions_plan` ADD CONSTRAINT `subscriptions_plan_provider_id_name_48ee031d_uniq` UNIQUE (`provider_id`, `name`);
ALTER TABLE `subscriptions_plan` ADD CONSTRAINT `subscriptions_plan_currency_id_2699a857_fk_subscript` FOREIGN KEY (`currency_id`) REFERENCES `subscriptions_currency` (`id`);
ALTER TABLE `subscriptions_plan` ADD CONSTRAINT `subscriptions_plan_provider_id_44311a78_fk_subscript` FOREIGN KEY (`provider_id`) REFERENCES `subscriptions_provider` (`id`);
ALTER TABLE `subscriptions_subscription` ADD CONSTRAINT `subscriptions_subscr_currency_id_ad6a44f1_fk_subscript` FOREIGN KEY (`currency_id`) REFERENCES `subscriptions_currency` (`id`);
ALTER TABLE `subscriptions_subscription` ADD CONSTRAINT `subscriptions_subscr_plan_id_2c895107_fk_subscript` FOREIGN KEY (`plan_id`) REFERENCES `subscriptions_plan` (`id`);
ALTER TABLE `subscriptions_subscription` ADD CONSTRAINT `subscriptions_subscr_provider_id_887c55a2_fk_subscript` FOREIGN KEY (`provider_id`) REFERENCES `subscriptions_provider` (`id`);
ALTER TABLE `subscriptions_subscription` ADD CONSTRAINT `subscriptions_subscription_user_id_a353e93d_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `subscriptions_payment` ADD CONSTRAINT `subscriptions_paymen_currency_id_4db2d703_fk_subscript` FOREIGN KEY (`currency_id`) REFERENCES `subscriptions_currency` (`id`);
ALTER TABLE `subscriptions_payment` ADD CONSTRAINT `subscriptions_payment_user_id_d337a89a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `subscriptions_payment` ADD CONSTRAINT `subscriptions_paymen_payment_method_id_28c17f14_fk_subscript` FOREIGN KEY (`payment_method_id`) REFERENCES `subscriptions_paymentmethod` (`id`);
ALTER TABLE `subscriptions_payment` ADD CONSTRAINT `subscriptions_paymen_subscription_id_f8df362c_fk_subscript` FOREIGN KEY (`subscription_id`) REFERENCES `subscriptions_subscription` (`id`);
ALTER TABLE `subscriptions_notification` ADD CONSTRAINT `subscriptions_notification_user_id_96b1f670_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `subscriptions_notification` ADD CONSTRAINT `subscriptions_notifi_subscription_id_38d3a95d_fk_subscript` FOREIGN KEY (`subscription_id`) REFERENCES `subscriptions_subscription` (`id`);
ALTER TABLE `subscriptions_comment` ADD CONSTRAINT `subscriptions_comment_user_id_0cd5f17e_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `subscriptions_comment` ADD CONSTRAINT `subscriptions_commen_subscription_id_43f5ae35_fk_subscript` FOREIGN KEY (`subscription_id`) REFERENCES `subscriptions_subscription` (`id`);
