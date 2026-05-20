-- Correction du bug core_userrole.role manquant
-- Ce script ajoute la colonne 'role' à la table core_userrole si elle n'existe pas

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='core_userrole' AND column_name='role'
    ) THEN
        ALTER TABLE core_userrole ADD COLUMN role VARCHAR(20);

        -- Commentaire optionnel pour expliquer la colonne
        COMMENT ON COLUMN core_userrole.role IS 'Rôle PostgreSQL utilisé pour les permissions PostgREST';
    END IF;
END $$;
