-- Migration SQL pour créer la table core_userrole
-- Exécutez ceci avec: psql -U postgres -d teraka -f create_userrole_table.sql

CREATE TABLE IF NOT EXISTS core_userrole (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT role_choices CHECK (role IN (
        'Expansion_L1',
        'Expansion_L2',
        'MRV_L1',
        'MRV_L2',
        'MRV_L3',
        'Admin_L1',
        'Admin_L2'
    ))
);

-- Créer des indices pour améliorer les performances
CREATE INDEX IF NOT EXISTS core_userrole_role_idx ON core_userrole(role);
CREATE INDEX IF NOT EXISTS core_userrole_user_id_idx ON core_userrole(user_id);

-- Afficher le résultat
\dt core_userrole
\d core_userrole
