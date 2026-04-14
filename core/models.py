# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class AnswerBienFaitAgroforesterieMembreSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_answer_bien_fait_agroforesterie_membre_suivi = models.UUIDField(unique=True)
    uuid_bien_fait_agroforesterie = models.ForeignKey('BienFaitAgroforesteries', models.DO_NOTHING, db_column='uuid_bien_fait_agroforesterie', to_field='uuid_bien')
    uuid_membre_suivi = models.ForeignKey('MembreSuivi', models.DO_NOTHING, db_column='uuid_membre_suivi', to_field='uuid_membre_suivi')

    class Meta:
        managed = False
        db_table = 'answer_bien_fait_agroforesterie_membre_suivi'


class AnswerCobeneficeArbreBosquetBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_baseline = models.ForeignKey('BosquetBaseline', models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')
    uuid_cobenefice_arbre = models.ForeignKey('CobeneficeArbres', models.DO_NOTHING, db_column='uuid_cobenefice_arbre', to_field='uuid_cobenefice_arbre')

    class Meta:
        managed = False
        db_table = 'answer_cobenefice_arbre_bosquet_baseline'


class AnswerCobeneficeArbreBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_suivi = models.ForeignKey('BosquetSuivi', models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')
    uuid_cobenefice_arbre = models.ForeignKey('CobeneficeArbres', models.DO_NOTHING, db_column='uuid_cobenefice_arbre', to_field='uuid_cobenefice_arbre')

    class Meta:
        managed = False
        db_table = 'answer_cobenefice_arbre_bosquet_suivi'


class AnswerCobeneficeArbreMembreSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_answer_cobenefice_arbre_membre_suivi = models.UUIDField(unique=True)
    uuid_cobenefice_arbre = models.ForeignKey('CobeneficeArbres', models.DO_NOTHING, db_column='uuid_cobenefice_arbre', to_field='uuid_cobenefice_arbre')
    uuid_membre_suivi = models.ForeignKey('MembreSuivi', models.DO_NOTHING, db_column='uuid_membre_suivi', to_field='uuid_membre_suivi')

    class Meta:
        managed = False
        db_table = 'answer_cobenefice_arbre_membre_suivi'


class AnswerInvasifBosquetBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_baseline = models.ForeignKey('BosquetBaseline', models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')
    uuid_invasif = models.ForeignKey('Invasifs', models.DO_NOTHING, db_column='uuid_invasif', to_field='uuid_invasif')

    class Meta:
        managed = False
        db_table = 'answer_invasif_bosquet_baseline'


class AnswerInvasifBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_suivi = models.ForeignKey('BosquetSuivi', models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')
    uuid_invasif = models.ForeignKey('Invasifs', models.DO_NOTHING, db_column='uuid_invasif', to_field='uuid_invasif')

    class Meta:
        managed = False
        db_table = 'answer_invasif_bosquet_suivi'


class AnswerLutteInvasifBosquetBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_baseline = models.ForeignKey('BosquetBaseline', models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')
    uuid_lutte_invasif = models.ForeignKey('LutteInvasifs', models.DO_NOTHING, db_column='uuid_lutte_invasif', to_field='uuid_lutte_invasif')

    class Meta:
        managed = False
        db_table = 'answer_lutte_invasif_bosquet_baseline'


class AnswerLutteInvasifBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_suivi = models.ForeignKey('BosquetSuivi', models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')
    uuid_lutte_invasif = models.ForeignKey('LutteInvasifs', models.DO_NOTHING, db_column='uuid_lutte_invasif', to_field='uuid_lutte_invasif')

    class Meta:
        managed = False
        db_table = 'answer_lutte_invasif_bosquet_suivi'


class AnswerLutteNuisibleBosquetBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_baseline = models.ForeignKey('BosquetBaseline', models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')
    uuid_lutte_nuisible = models.ForeignKey('LutteNuisibles', models.DO_NOTHING, db_column='uuid_lutte_nuisible', to_field='uuid_lutte_nuisible')

    class Meta:
        managed = False
        db_table = 'answer_lutte_nuisible_bosquet_baseline'


class AnswerLutteNuisibleBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_suivi = models.ForeignKey('BosquetSuivi', models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')
    uuid_lutte_nuisible = models.ForeignKey('LutteNuisibles', models.DO_NOTHING, db_column='uuid_lutte_nuisible', to_field='uuid_lutte_nuisible')

    class Meta:
        managed = False
        db_table = 'answer_lutte_nuisible_bosquet_suivi'


class AnswerNuisibleBosquetBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_baseline = models.ForeignKey('BosquetBaseline', models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')
    uuid_nuisible = models.ForeignKey('Nuisibles', models.DO_NOTHING, db_column='uuid_nuisible', to_field='uuid_nuisible')

    class Meta:
        managed = False
        db_table = 'answer_nuisible_bosquet_baseline'


class AnswerNuisibleBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_suivi = models.ForeignKey('BosquetSuivi', models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')
    uuid_nuisible = models.ForeignKey('Nuisibles', models.DO_NOTHING, db_column='uuid_nuisible', to_field='uuid_nuisible')

    class Meta:
        managed = False
        db_table = 'answer_nuisible_bosquet_suivi'


class AnswerProduitArbreBosquetBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_baseline = models.ForeignKey('BosquetBaseline', models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')
    uuid_produit_arbre = models.ForeignKey('ProduitsArbres', models.DO_NOTHING, db_column='uuid_produit_arbre', to_field='uuid_produit_arbre')

    class Meta:
        managed = False
        db_table = 'answer_produit_arbre_bosquet_baseline'


class AnswerProduitArbreBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_suivi = models.ForeignKey('BosquetSuivi', models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')
    uuid_produit_arbre = models.ForeignKey('ProduitsArbres', models.DO_NOTHING, db_column='uuid_produit_arbre', to_field='uuid_produit_arbre')

    class Meta:
        managed = False
        db_table = 'answer_produit_arbre_bosquet_suivi'


class AnswerProduitArbreMembreSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_answer_produit_arbre_membre_suivi = models.UUIDField(unique=True)
    uuid_produit_arbre = models.ForeignKey('ProduitsArbres', models.DO_NOTHING, db_column='uuid_produit_arbre', to_field='uuid_produit_arbre')
    uuid_membre_suivi = models.ForeignKey('MembreSuivi', models.DO_NOTHING, db_column='uuid_membre_suivi', to_field='uuid_membre_suivi')

    class Meta:
        managed = False
        db_table = 'answer_produit_arbre_membre_suivi'


class AnswerSolActuelBosquetBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_baseline = models.ForeignKey('BosquetBaseline', models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')
    uuid_sol_use = models.ForeignKey('UtilisationSolBosquets', models.DO_NOTHING, db_column='uuid_sol_use', to_field='uuid_sol_use')

    class Meta:
        managed = False
        db_table = 'answer_sol_actuel_bosquet_baseline'


class AnswerSolActuelBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_suivi = models.ForeignKey('BosquetSuivi', models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')
    uuid_sol_use = models.ForeignKey('UtilisationSolBosquets', models.DO_NOTHING, db_column='uuid_sol_use', to_field='uuid_sol_use')

    class Meta:
        managed = False
        db_table = 'answer_sol_actuel_bosquet_suivi'


class AnswerSourcingGraineArbreBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_answer_sourcing_graine_arbre_baseline = models.UUIDField(unique=True)
    uuid_arbre_baseline = models.ForeignKey('ArbreBaseline', models.DO_NOTHING, db_column='uuid_arbre_baseline', to_field='uuid_arbre_baseline')
    uuid_sourcing_graine = models.ForeignKey('SourcingGraines', models.DO_NOTHING, db_column='uuid_sourcing_graine', to_field='uuid_graine')

    class Meta:
        managed = False
        db_table = 'answer_sourcing_graine_arbre_baseline'


class AnswerSourcingGraineArbreSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_answer_sourcing_graine_arbre_suivi = models.UUIDField(unique=True)
    uuid_arbre_suivi = models.ForeignKey('ArbreSuivi', models.DO_NOTHING, db_column='uuid_arbre_suivi', to_field='uuid_arbre_suivi')
    uuid_sourcing_graine = models.ForeignKey('SourcingGraines', models.DO_NOTHING, db_column='uuid_sourcing_graine', to_field='uuid_graine')

    class Meta:
        managed = False
        db_table = 'answer_sourcing_graine_arbre_suivi'


class AnswerSourcingPlantArbreBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_answer_sourcing_plant_arbre_baseline = models.UUIDField(unique=True)
    uuid_arbre_baseline = models.ForeignKey('ArbreBaseline', models.DO_NOTHING, db_column='uuid_arbre_baseline', to_field='uuid_arbre_baseline')
    uuid_sourcing_plant = models.ForeignKey('SourcingPlants', models.DO_NOTHING, db_column='uuid_sourcing_plant', to_field='uuid_plant')

    class Meta:
        managed = False
        db_table = 'answer_sourcing_plant_arbre_baseline'


class AnswerSourcingPlantArbreSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_answer_sourcing_plant_arbre_suivi = models.UUIDField(unique=True)
    uuid_arbre_suivi = models.ForeignKey('ArbreSuivi', models.DO_NOTHING, db_column='uuid_arbre_suivi', to_field='uuid_arbre_suivi')
    uuid_sourcing_plant = models.ForeignKey('SourcingPlants', models.DO_NOTHING, db_column='uuid_sourcing_plant', to_field='uuid_plant')

    class Meta:
        managed = False
        db_table = 'answer_sourcing_plant_arbre_suivi'


class AnswerUtilisationArbreBosquetBaseline(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_baseline = models.ForeignKey('BosquetBaseline', models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')
    uuid_utilisation_arbre = models.ForeignKey('UtilisationArbres', models.DO_NOTHING, db_column='uuid_utilisation_arbre', to_field='uuid_utilisation_arbre')

    class Meta:
        managed = False
        db_table = 'answer_utilisation_arbre_bosquet_baseline'


class AnswerUtilisationArbreBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_suivi = models.ForeignKey('BosquetSuivi', models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')
    uuid_utilisation_arbre = models.ForeignKey('UtilisationArbres', models.DO_NOTHING, db_column='uuid_utilisation_arbre', to_field='uuid_utilisation_arbre')

    class Meta:
        managed = False
        db_table = 'answer_utilisation_arbre_bosquet_suivi'


class ArbreBaseline(models.Model):
    uuid_arbre_baseline = models.UUIDField(unique=True)
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_arbre_gps = models.OneToOneField('ArbreGps', models.DO_NOTHING, db_column='uuid_arbre_gps')
    date_baseline = models.DateTimeField()
    uuid_espece = models.ForeignKey('EspecesArbres', models.DO_NOTHING, db_column='uuid_espece', to_field='uuid_espece', blank=True, null=True)
    autre_espece = models.TextField(blank=True, null=True)
    sourcing = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    annee_plantation = models.IntegerField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'arbre_baseline'


class ArbreGps(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_arbre_gps = models.UUIDField(unique=True)
    uuid_bosquet_gps = models.ForeignKey('BosquetGps', models.DO_NOTHING, db_column='uuid_bosquet_gps', to_field='uuid_bosquet_gps')
    geom = models.PointField(srid=32738)
    numero_arbre = models.IntegerField()
    statut_arbre = models.TextField()

    class Meta:
        managed = False
        db_table = 'arbre_gps'


class ArbreSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_arbre_suivi = models.UUIDField(unique=True)
    uuid_arbre_gps = models.ForeignKey(ArbreGps, models.DO_NOTHING, db_column='uuid_arbre_gps', to_field='uuid_arbre_gps')
    date_suivi = models.DateTimeField()
    uuid_espece = models.ForeignKey('EspecesArbres', models.DO_NOTHING, db_column='uuid_espece', to_field='uuid_espece', blank=True, null=True)
    autre_espece = models.TextField(blank=True, null=True)
    sourcing = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    annee_plantation = models.IntegerField(blank=True, null=True)
    statut_arbre = models.TextField()
    echantillon = models.BooleanField()
    multitiges = models.BooleanField(blank=True, null=True)
    circonference = models.FloatField(blank=True, null=True)
    hauteur = models.FloatField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'arbre_suivi'


class AuditLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    table_name = models.TextField()
    operation = models.TextField()
    record_id = models.TextField(blank=True, null=True)
    user_id = models.TextField(blank=True, null=True)
    action_time = models.DateTimeField()
    old_data = models.JSONField(blank=True, null=True)
    new_data = models.JSONField(blank=True, null=True)
    previous_hash = models.TextField(blank=True, null=True)
    current_hash = models.TextField()

    class Meta:
        managed = False
        db_table = 'audit_log'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BienFaitAgroforesteries(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_bien = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'bien_fait_agroforesteries'


class BosquetBaseline(models.Model):
    uuid_bosquet_baseline = models.UUIDField(unique=True)
    uuid_bosquet_gps = models.OneToOneField('BosquetGps', models.DO_NOTHING, db_column='uuid_bosquet_gps')
    uuid_operateur = models.UUIDField()
    uuid_verificateur = models.UUIDField()
    operateur_id = models.TextField()
    c_com = models.IntegerField()
    date_baseline = models.DateTimeField()
    proprietaire = models.BooleanField(blank=True, null=True)
    nom_proprietaire = models.TextField(blank=True, null=True)
    lien_usufruitier = models.TextField(blank=True, null=True)
    preuve_autorisation = models.BooleanField(blank=True, null=True)
    demarche_autorisation = models.TextField(blank=True, null=True)
    usufruitier = models.TextField(blank=True, null=True)
    preuve_foncier = models.BooleanField(blank=True, null=True)
    demarche_fonciere = models.TextField(blank=True, null=True)
    statut_foncier = models.TextField(blank=True, null=True)
    foncier_legal = models.TextField(blank=True, null=True)
    foncier_coutumier = models.TextField(blank=True, null=True)
    conflit_foncier = models.BooleanField(blank=True, null=True)
    type_conflit_pers = models.TextField(blank=True, null=True)
    arbre_plantes = models.IntegerField(blank=True, null=True)
    arbre_vivants = models.IntegerField(blank=True, null=True)
    taux_survie = models.IntegerField(blank=True, null=True)
    objectif_plantation_saison = models.IntegerField(blank=True, null=True)
    objectif_plantation_5_annee = models.IntegerField(blank=True, null=True)
    pepiniere_individuelle = models.BooleanField(blank=True, null=True)
    plants = models.IntegerField(blank=True, null=True)
    compost_org = models.BooleanField(blank=True, null=True)
    intrant_chimique = models.BooleanField(blank=True, null=True)
    nuisible = models.BooleanField(blank=True, null=True)
    invasif = models.BooleanField(blank=True, null=True)
    foret_1ha = models.BooleanField(blank=True, null=True)
    surface_boisee_ha = models.FloatField(blank=True, null=True)
    foret_voisine = models.BooleanField(blank=True, null=True)
    distance_foret_m = models.IntegerField(blank=True, null=True)
    deforestation_10ans = models.BooleanField(blank=True, null=True)
    justif_def = models.TextField(blank=True, null=True)
    annee_defor = models.IntegerField(blank=True, null=True)
    souches_arbres_recentes = models.BooleanField(blank=True, null=True)
    nbre_souches_recentes = models.IntegerField(blank=True, null=True)
    zone_humide = models.BooleanField(blank=True, null=True)
    zone_habitee = models.BooleanField(blank=True, null=True)
    paturage = models.BooleanField(blank=True, null=True)
    topographie = models.ForeignKey('Topographies', models.DO_NOTHING, db_column='topographie', to_field='uuid_topo', blank=True, null=True)
    couleur_sol = models.ForeignKey('SolCouleurs', models.DO_NOTHING, db_column='couleur_sol', to_field='uuid_sol_couleur', blank=True, null=True)
    type_sol = models.ForeignKey('SolTypes', models.DO_NOTHING, db_column='type_sol', to_field='uuid_sol_type', blank=True, null=True)
    zone_riparienne = models.BooleanField(blank=True, null=True)
    cultures_annuelles = models.IntegerField(blank=True, null=True)
    cultures_perennes = models.IntegerField(blank=True, null=True)
    arbres = models.IntegerField(blank=True, null=True)
    litiere = models.IntegerField(blank=True, null=True)
    arbuste = models.IntegerField(blank=True, null=True)
    herbe = models.IntegerField(blank=True, null=True)
    zone_nue = models.IntegerField(blank=True, null=True)
    total_couverture_sol = models.IntegerField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bosquet_baseline'


class BosquetEvenement(models.Model):
    uuid_bosquet_evenement = models.UUIDField(unique=True)
    uuid_verificateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_verificateur', to_field='uuid_user', blank=True, null=True)
    uuid_operateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_operateur', to_field='uuid_user', related_name='bosquetevenement_uuid_operateur_set', blank=True, null=True)
    operateur_id = models.TextField(blank=True, null=True)
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com', blank=True, null=True)
    uuid_bosquet_gps = models.ForeignKey('BosquetGps', models.DO_NOTHING, db_column='uuid_bosquet_gps', to_field='uuid_bosquet_gps')
    uuid_membre_source = models.ForeignKey('Membre', models.DO_NOTHING, db_column='uuid_membre_source', to_field='uuid_membre')
    uuid_membre_cible = models.ForeignKey('Membre', models.DO_NOTHING, db_column='uuid_membre_cible', to_field='uuid_membre', related_name='bosquetevenement_uuid_membre_cible_set', blank=True, null=True)
    uuid_nouveau_membre = models.ForeignKey('PgNouveauMembre', models.DO_NOTHING, db_column='uuid_nouveau_membre', to_field='uuid_membre', blank=True, null=True)
    date_evenement = models.DateTimeField()
    type_evenement = models.TextField()
    statut_resultant = models.TextField()
    type_membre = models.TextField()
    exist_event_doc = models.BooleanField(blank=True, null=True)
    statut_validation = models.TextField(blank=True, null=True)
    date_validation = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bosquet_evenement'


class BosquetEvenementDocument(models.Model):
    operateur_id = models.TextField(blank=True, null=True)
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com', blank=True, null=True)
    uuid_bosquet_evenement_doc = models.UUIDField(unique=True)
    uuid_bosquet_evenement = models.OneToOneField(BosquetEvenement, models.DO_NOTHING, db_column='uuid_bosquet_evenement')
    type_document = models.TextField()
    detail_autre = models.TextField(blank=True, null=True)
    date_document = models.DateTimeField()
    lien_document = models.TextField(blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bosquet_evenement_document'


class BosquetGeomHistorique(models.Model):
    uuid_bosquet_geom_historique = models.UUIDField(unique=True)
    geom = models.PolygonField(srid=32738)
    uuid_bosquet_gps = models.ForeignKey('BosquetGps', models.DO_NOTHING, db_column='uuid_bosquet_gps', to_field='uuid_bosquet_gps')
    uuid_operateur = models.UUIDField()
    uuid_verificateur = models.UUIDField()
    area_ha = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bosquet_geom_historique'


class BosquetGps(models.Model):
    uuid_bosquet_gps = models.UUIDField(unique=True)
    uuid_membre = models.ForeignKey('Membre', models.DO_NOTHING, db_column='uuid_membre', to_field='uuid_membre')
    uuid_operateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_operateur', to_field='uuid_user', blank=True, null=True)
    uuid_verificateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_verificateur', to_field='uuid_user', related_name='bosquetgps_uuid_verificateur_set', blank=True, null=True)
    uuid_pg = models.ForeignKey('PgInfos', models.DO_NOTHING, db_column='uuid_pg', to_field='uuid_pg')
    operateur_id = models.UUIDField(blank=True, null=True)
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    num_bosquet = models.TextField()
    code_bosquet = models.TextField()
    statut_bosquet = models.TextField()
    date_statut = models.DateTimeField()
    area_ha = models.FloatField(blank=True, null=True)
    date_creation = models.DateTimeField()
    geom = models.PolygonField(srid=32738)

    class Meta:
        managed = False
        db_table = 'bosquet_gps'


class BosquetPhotoDocument(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey('Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_bosquet_photo_doc = models.UUIDField(unique=True)
    uuid_bosquet_evenement_doc = models.ForeignKey(BosquetEvenementDocument, models.DO_NOTHING, db_column='uuid_bosquet_evenement_doc', to_field='uuid_bosquet_evenement_doc')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bosquet_photo_document'


class BosquetSuivi(models.Model):
    uuid_bosquet_suivi = models.UUIDField(unique=True)
    uuid_bosquet_gps = models.ForeignKey(BosquetGps, models.DO_NOTHING, db_column='uuid_bosquet_gps', to_field='uuid_bosquet_gps')
    date_suivi = models.DateTimeField()
    uuid_operateur = models.UUIDField()
    uuid_verificateur = models.UUIDField()
    operateur_id = models.TextField()
    c_com = models.IntegerField()
    date_baseline = models.DateTimeField()
    modif_bosquet = models.BooleanField(blank=True, null=True)
    changement_propriete = models.BooleanField(blank=True, null=True)
    proprietaire = models.BooleanField(blank=True, null=True)
    nom_proprietaire = models.TextField(blank=True, null=True)
    lien_usufruitier = models.TextField(blank=True, null=True)
    avance_demarche_fonciere = models.BooleanField(blank=True, null=True)
    preuve_autorisation = models.BooleanField(blank=True, null=True)
    preuve_foncier = models.BooleanField(blank=True, null=True)
    statut_foncier = models.TextField(blank=True, null=True)
    foncier_legal = models.TextField(blank=True, null=True)
    foncier_coutumier = models.TextField(blank=True, null=True)
    conflit_foncier = models.BooleanField(blank=True, null=True)
    type_conflit_pers = models.TextField(blank=True, null=True)
    arbre_plantes = models.IntegerField(blank=True, null=True)
    arbre_vivants = models.IntegerField(blank=True, null=True)
    taux_survie = models.IntegerField(blank=True, null=True)
    objectif_plantation_saison = models.IntegerField(blank=True, null=True)
    objectif_plantation_5_annee = models.IntegerField(blank=True, null=True)
    pepiniere_individuelle = models.BooleanField(blank=True, null=True)
    plants = models.IntegerField(blank=True, null=True)
    compost_org = models.BooleanField(blank=True, null=True)
    intrant_chimique = models.BooleanField(blank=True, null=True)
    nuisible = models.BooleanField(blank=True, null=True)
    invasif = models.BooleanField(blank=True, null=True)
    paturage = models.BooleanField(blank=True, null=True)
    couleur_sol = models.ForeignKey('SolCouleurs', models.DO_NOTHING, db_column='couleur_sol', to_field='uuid_sol_couleur', blank=True, null=True)
    type_sol = models.ForeignKey('SolTypes', models.DO_NOTHING, db_column='type_sol', to_field='uuid_sol_type', blank=True, null=True)
    cultures_annuelles = models.IntegerField(blank=True, null=True)
    cultures_perennes = models.IntegerField(blank=True, null=True)
    arbres = models.IntegerField(blank=True, null=True)
    litiere = models.IntegerField(blank=True, null=True)
    arbuste = models.IntegerField(blank=True, null=True)
    herbe = models.IntegerField(blank=True, null=True)
    zone_nue = models.IntegerField(blank=True, null=True)
    total_couverture_sol = models.IntegerField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bosquet_suivi'


class CobeneficeArbres(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_cobenefice_arbre = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'cobenefice_arbres'


class Communes(models.Model):
    uuid_com = models.UUIDField(unique=True)
    c_com = models.IntegerField(unique=True)
    geom = models.PolygonField(srid=32738)
    region = models.TextField()
    district = models.TextField()
    commune = models.TextField()

    class Meta:
        managed = False
        db_table = 'communes'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EspecesArbres(models.Model):
    genre = models.TextField(blank=True, null=True)
    espece = models.TextField(blank=True, null=True)
    nom_vernaculaire = models.TextField(blank=True, null=True)
    appellation_locale = models.TextField(blank=True, null=True)
    familles_botanique = models.TextField(blank=True, null=True)
    categorie = models.TextField(blank=True, null=True)
    liste_rouge = models.BooleanField()
    liste_verte = models.BooleanField()
    liste_blanche = models.BooleanField()
    uuid_espece = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'especes_arbres'


class Formations(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_formation = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'formations'


class Invasifs(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_invasif = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'invasifs'


class LutteInvasifs(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_lutte_invasif = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'lutte_invasifs'


class LutteNuisibles(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_lutte_nuisible = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'lutte_nuisibles'


class Membre(models.Model):
    uuid_membre = models.UUIDField(unique=True)
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_operateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_operateur', to_field='uuid_user', blank=True, null=True)
    uuid_verificateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_verificateur', to_field='uuid_user', related_name='membre_uuid_verificateur_set', blank=True, null=True)
    date_saisie = models.DateTimeField()
    uuid_pg = models.ForeignKey('PgInfos', models.DO_NOTHING, db_column='uuid_pg', to_field='uuid_pg')
    code_pg = models.TextField()
    nom_pg = models.TextField()
    statut_membre = models.TextField()
    date_statut = models.DateTimeField()
    fokontany = models.TextField(blank=True, null=True)
    village = models.TextField(blank=True, null=True)
    nom_membre = models.TextField()
    prenom_membre = models.TextField(blank=True, null=True)
    nom_prenom_membre = models.TextField(blank=True, null=True)
    genre = models.TextField()
    annee_naissance = models.IntegerField(blank=True, null=True)
    cin = models.TextField(blank=True, null=True)
    tel = models.TextField(blank=True, null=True)
    annee_inscription = models.IntegerField()
    lieu_inscription = models.TextField(blank=True, null=True)
    date_contractualisation = models.DateTimeField(blank=True, null=True)
    pepinieriste = models.BooleanField()
    leader = models.BooleanField()
    agent_cluster = models.BooleanField()
    quantificateur = models.BooleanField()
    deforestation = models.BooleanField()
    annee_deforestation = models.IntegerField(blank=True, null=True)
    zone_riparienne = models.BooleanField()
    arbres_sup_10pct = models.BooleanField()
    liste_arbres = models.TextField(blank=True, null=True)
    utilisation_arbres = models.TextField(blank=True, null=True)
    plantation_arbres_1an = models.IntegerField(blank=True, null=True)
    plantation_arbres_5ans = models.IntegerField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'membre'


class MembreInscrit(models.Model):
    uuid_membre = models.UUIDField(unique=True)
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_operateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_operateur', to_field='uuid_user', blank=True, null=True)
    date_saisie = models.DateTimeField()
    date_inscription = models.DateTimeField()
    date_qualification = models.DateTimeField(blank=True, null=True)
    date_contractualisation = models.DateTimeField(blank=True, null=True)
    statut_inscrit = models.TextField()
    fokontany = models.TextField(blank=True, null=True)
    village = models.TextField(blank=True, null=True)
    nom_membre = models.TextField()
    prenom_membre = models.TextField(blank=True, null=True)
    nom_prenom_membre = models.TextField(blank=True, null=True)
    genre = models.TextField()
    annee_naissance = models.IntegerField(blank=True, null=True)
    cin = models.TextField(blank=True, null=True)
    tel = models.TextField(blank=True, null=True)
    annee_inscription = models.IntegerField()
    lieu_inscription = models.TextField(blank=True, null=True)
    pepinieriste = models.BooleanField()
    leader = models.BooleanField()
    agent_cluster = models.BooleanField()
    quantificateur = models.BooleanField()
    deforestation = models.BooleanField()
    annee_deforestation = models.IntegerField(blank=True, null=True)
    zone_riparienne = models.BooleanField()
    arbres_sup_10pct = models.BooleanField()
    liste_arbres = models.TextField(blank=True, null=True)
    utilisation_arbres = models.TextField(blank=True, null=True)
    nombre_arbres_prevus = models.IntegerField(blank=True, null=True)
    nombre_arbre_5ans = models.IntegerField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'membre_inscrit'


class MembreSuivi(models.Model):
    uuid_membre_suivi = models.UUIDField(unique=True)
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_operateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_operateur', to_field='uuid_user', blank=True, null=True)
    uuid_verificateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_verificateur', to_field='uuid_user', related_name='membresuivi_uuid_verificateur_set', blank=True, null=True)
    uuid_membre = models.ForeignKey(Membre, models.DO_NOTHING, db_column='uuid_membre', to_field='uuid_membre')
    date_suivi = models.DateTimeField()
    annee = models.IntegerField()
    revenu_annuel_estime = models.FloatField()
    revenu_teraka = models.FloatField()
    frequence_penurie_alimentaire = models.TextField()
    qualite_recolte = models.TextField()
    pratiques_csa = models.BooleanField()
    foyers_ameliore = models.BooleanField()
    nombre_foyers_ameliore = models.IntegerField(blank=True, null=True)
    temps_collecte_bois = models.IntegerField(blank=True, null=True)
    pratique_agroforesterie = models.BooleanField()
    nouvelle_pratique_agroforesterie = models.BooleanField()
    ressent_bienfaits_agroforesterie = models.BooleanField()
    difficulte_programme = models.BooleanField()
    difficulte_commentaire = models.TextField()
    risque_erosion_inondation = models.TextField()
    bien_etre_general = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'membre_suivi'


class Nuisibles(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_nuisible = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'nuisibles'


class PaiementMembre(models.Model):
    uuid_paiement_membre = models.UUIDField(unique=True)
    uuid_paiement_pg = models.ForeignKey('PaiementPg', models.DO_NOTHING, db_column='uuid_paiement_pg', to_field='uuid_paiement_pg')
    uuid_membre = models.ForeignKey(Membre, models.DO_NOTHING, db_column='uuid_membre', to_field='uuid_membre')
    prix_unitaire_liste_verte = models.FloatField()
    prix_unitaire_liste_grise_blanche_noire = models.FloatField()
    nbr_arbre_liste_verte = models.IntegerField()
    nbr_arbre_liste_grise = models.IntegerField()
    nbr_arbre_liste_blanche = models.IntegerField()
    nbr_arbre_liste_noire = models.IntegerField()
    commentaire = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paiement_membre'


class PaiementPg(models.Model):
    uuid_paiement_pg = models.UUIDField(unique=True)
    uuid_pg = models.ForeignKey('PgInfos', models.DO_NOTHING, db_column='uuid_pg', to_field='uuid_pg')
    code_pg = models.TextField()
    nom_pg = models.TextField()
    reference_facture = models.TextField()
    date_paiement = models.DateTimeField()
    date_demande = models.DateTimeField(blank=True, null=True)
    date_verification = models.DateTimeField(blank=True, null=True)
    uuid_operateur = models.UUIDField(blank=True, null=True)
    uuid_verificateur = models.UUIDField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paiement_pg'


class PaiementPgHistorique(models.Model):
    uuid_paiement_pg_historique = models.UUIDField(unique=True)
    uuid_paiement_pg = models.ForeignKey(PaiementPg, models.DO_NOTHING, db_column='uuid_paiement_pg', to_field='uuid_paiement_pg')
    uuid_operateur = models.UUIDField()
    statut = models.TextField()
    date_statut = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'paiement_pg_historique'


class PgDocument(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_pg_document = models.UUIDField(unique=True)
    uuid_pg_historique = models.OneToOneField('PgStatutHistorique', models.DO_NOTHING, db_column='uuid_pg_historique')
    type_document = models.TextField()

    class Meta:
        managed = False
        db_table = 'pg_document'


class PgGps(models.Model):
    uuid_pg_gps = models.UUIDField(unique=True)
    geom = models.PointField(srid=32738)
    uuid_pg = models.OneToOneField('PgInfos', models.DO_NOTHING, db_column='uuid_pg')
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    operateur_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pg_gps'


class PgInfos(models.Model):
    uuid_pg = models.UUIDField(unique=True)
    uuid_operateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_operateur', to_field='uuid_user', blank=True, null=True)
    uuid_verificateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_verificateur', to_field='uuid_user', related_name='pginfos_uuid_verificateur_set', blank=True, null=True)
    date_saisie = models.DateTimeField()
    date_verification = models.DateTimeField(blank=True, null=True)
    operateur_id = models.TextField(blank=True, null=True)
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    code_pg = models.TextField()
    nom_pg = models.TextField()
    nom_cluster = models.TextField(blank=True, null=True)
    fokontany = models.TextField(blank=True, null=True)
    village = models.TextField(blank=True, null=True)
    date_inscription = models.DateTimeField()
    annee_inscription = models.IntegerField()
    lieu_inscription = models.TextField(blank=True, null=True)
    date_contrat_ges = models.DateTimeField(blank=True, null=True)
    statut_pg = models.TextField()
    date_statut = models.DateTimeField(blank=True, null=True)
    representant_pg = models.TextField(blank=True, null=True)
    contact_representant_pg = models.TextField(blank=True, null=True)
    objectif_plantation_5_ans = models.IntegerField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pg_infos'


class PgMembreEvenement(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_membre_event = models.UUIDField(unique=True)
    uuid_pg_suivi_admin = models.ForeignKey('PgSuiviAdmin', models.DO_NOTHING, db_column='uuid_pg_suivi_admin', to_field='uuid_suivi_admin')

    class Meta:
        managed = False
        db_table = 'pg_membre_evenement'


class PgNouveauMembre(models.Model):
    uuid_membre = models.UUIDField(unique=True)
    operateur_id = models.TextField(blank=True, null=True)
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_pg_membre_event = models.ForeignKey(PgMembreEvenement, models.DO_NOTHING, db_column='uuid_pg_membre_event', to_field='uuid_membre_event')
    uuid_operateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_operateur', to_field='uuid_user', blank=True, null=True)
    uuid_verificateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_verificateur', to_field='uuid_user', related_name='pgnouveaumembre_uuid_verificateur_set', blank=True, null=True)
    date_saisie = models.DateTimeField()
    uuid_pg = models.ForeignKey(PgInfos, models.DO_NOTHING, db_column='uuid_pg', to_field='uuid_pg')
    code_pg = models.TextField()
    nom_pg = models.TextField()
    statut_membre = models.TextField()
    date_statut = models.DateTimeField()
    fokontany = models.TextField(blank=True, null=True)
    village = models.TextField(blank=True, null=True)
    nom_membre = models.TextField()
    prenom_membre = models.TextField(blank=True, null=True)
    nom_prenom_membre = models.TextField(blank=True, null=True)
    genre = models.TextField()
    annee_naissance = models.IntegerField(blank=True, null=True)
    cin = models.TextField(blank=True, null=True)
    tel = models.TextField(blank=True, null=True)
    annee_inscription = models.IntegerField()
    lieu_inscription = models.TextField(blank=True, null=True)
    statut_validation = models.TextField(blank=True, null=True)
    date_validation = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pg_nouveau_membre'


class PgPhoto(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_photo = models.UUIDField(unique=True)
    uuid_pg_suivi = models.ForeignKey('PgSuivi', models.DO_NOTHING, db_column='uuid_pg_suivi', to_field='uuid_suivi')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pg_photo'


class PgPhotoDocument(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_photo_document = models.UUIDField(unique=True)
    uuid_pg_document = models.ForeignKey(PgDocument, models.DO_NOTHING, db_column='uuid_pg_document', to_field='uuid_pg_document')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pg_photo_document'


class PgStatutHistorique(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_pg_historique = models.UUIDField(unique=True)
    uuid_pg = models.ForeignKey(PgInfos, models.DO_NOTHING, db_column='uuid_pg', to_field='uuid_pg')
    uuid_suivi_admin = models.OneToOneField('PgSuiviAdmin', models.DO_NOTHING, db_column='uuid_suivi_admin')

    class Meta:
        managed = False
        db_table = 'pg_statut_historique'


class PgSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_suivi = models.UUIDField(unique=True)
    uuid_pg_gps = models.ForeignKey(PgGps, models.DO_NOTHING, db_column='uuid_pg_gps', to_field='uuid_pg_gps')
    date_suivi = models.DateTimeField()
    trois_familles = models.BooleanField()
    membre_pg_6_12 = models.BooleanField()
    nbre_membre_pg = models.IntegerField(blank=True, null=True)
    group_2ha_min = models.BooleanField()
    autre_projet_carbone = models.BooleanField()
    nom_autre_projet_teraka = models.TextField(blank=True, null=True)
    projet_non_carbone = models.BooleanField()
    nom_projet_non_carbone = models.TextField(blank=True, null=True)
    pg_eligble = models.BooleanField()
    arbres_plantes = models.IntegerField()
    objectf_plantation_5_ans = models.IntegerField()
    pepiniere = models.BooleanField()
    plan_plantation = models.BooleanField()
    visite_bosquet = models.BooleanField()
    reunion_pg = models.BooleanField()
    reunion_cluster = models.BooleanField()
    formation_cluster = models.BooleanField()
    valeurs_teraka = models.BooleanField()
    regles_eligibilite = models.BooleanField()
    alert = models.BooleanField()
    doleance = models.BooleanField()
    detail_alert_doleance = models.TextField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pg_suivi'


class PgSuiviAdmin(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    uuid_suivi_admin = models.UUIDField(unique=True)
    uuid_pg_suivi = models.OneToOneField(PgSuivi, models.DO_NOTHING, db_column='uuid_pg_suivi')
    uuid_verificateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_verificateur', to_field='uuid_user', blank=True, null=True)
    uuid_operateur = models.ForeignKey('Users', models.DO_NOTHING, db_column='uuid_operateur', to_field='uuid_user', related_name='pgsuiviadmin_uuid_operateur_set', blank=True, null=True)
    modif_compo_pg = models.BooleanField()
    statut_change = models.BooleanField()
    reprensentant_pg = models.TextField(blank=True, null=True)
    contact_representant_pg = models.TextField(blank=True, null=True)
    mobile_banking = models.BooleanField()
    no_mobile_banking = models.TextField(blank=True, null=True)
    titulaire_compte_mobile_banking = models.TextField(blank=True, null=True)
    statut_validation = models.TextField(blank=True, null=True)
    date_validation = models.DateTimeField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pg_suivi_admin'


class PhotoAutorisationBosquet(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)
    uuid_bosquet_baseline = models.ForeignKey(BosquetBaseline, models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')

    class Meta:
        managed = False
        db_table = 'photo_autorisation_bosquet'


class PhotoAutorisationBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)
    uuid_bosquet_suivi = models.ForeignKey(BosquetSuivi, models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')

    class Meta:
        managed = False
        db_table = 'photo_autorisation_bosquet_suivi'


class PhotoAutreEspeceArbreBaseline(models.Model):
    uuid_autre_espece_arbre_baseline = models.UUIDField(unique=True)
    uuid_arbre_baseline = models.ForeignKey(ArbreBaseline, models.DO_NOTHING, db_column='uuid_arbre_baseline', to_field='uuid_arbre_baseline')
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'photo_autre_espece_arbre_baseline'


class PhotoAutreEspeceArbreSuivi(models.Model):
    uuid_autre_espece_arbre_suivi = models.UUIDField(unique=True)
    uuid_arbre_suivi = models.ForeignKey(ArbreSuivi, models.DO_NOTHING, db_column='uuid_arbre_suivi', to_field='uuid_arbre_suivi')
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'photo_autre_espece_arbre_suivi'


class PhotoBosquet(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)
    uuid_bosquet_baseline = models.ForeignKey(BosquetBaseline, models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')

    class Meta:
        managed = False
        db_table = 'photo_bosquet'


class PhotoBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)
    uuid_bosquet_suivi = models.ForeignKey(BosquetSuivi, models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')

    class Meta:
        managed = False
        db_table = 'photo_bosquet_suivi'


class PhotoDocFoncierBosquet(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)
    uuid_bosquet_baseline = models.ForeignKey(BosquetBaseline, models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')

    class Meta:
        managed = False
        db_table = 'photo_doc_foncier_bosquet'


class PhotoDocFoncierBosquetSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)
    uuid_bosquet_suivi = models.ForeignKey(BosquetSuivi, models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')

    class Meta:
        managed = False
        db_table = 'photo_doc_foncier_bosquet_suivi'


class PhotoListeRougeArbreBaseline(models.Model):
    uuid_liste_rouge_arbre_baseline = models.UUIDField(unique=True)
    uuid_arbre_baseline = models.ForeignKey(ArbreBaseline, models.DO_NOTHING, db_column='uuid_arbre_baseline', to_field='uuid_arbre_baseline')
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'photo_liste_rouge_arbre_baseline'


class PhotoListeRougeArbreSuivi(models.Model):
    uuid_liste_rouge_arbre_suivi = models.UUIDField(unique=True)
    uuid_arbre_suivi = models.ForeignKey(ArbreSuivi, models.DO_NOTHING, db_column='uuid_arbre_suivi', to_field='uuid_arbre_suivi')
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'photo_liste_rouge_arbre_suivi'


class PhotoPepiniere(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)
    uuid_bosquet_baseline = models.ForeignKey(BosquetBaseline, models.DO_NOTHING, db_column='uuid_bosquet_baseline', to_field='uuid_bosquet_baseline')

    class Meta:
        managed = False
        db_table = 'photo_pepiniere'


class PhotoPepiniereSuivi(models.Model):
    operateur_id = models.TextField()
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com')
    chemin = models.TextField()
    external_url = models.TextField(blank=True, null=True)
    uuid_bosquet_suivi = models.ForeignKey(BosquetSuivi, models.DO_NOTHING, db_column='uuid_bosquet_suivi', to_field='uuid_bosquet_suivi')

    class Meta:
        managed = False
        db_table = 'photo_pepiniere_suivi'


class ProduitsArbres(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_produit_arbre = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'produits_arbres'


class SolCouleurs(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_sol_couleur = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'sol_couleurs'


class SolTypes(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_sol_type = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'sol_types'


class SourcingGraines(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_graine = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'sourcing_graines'


class SourcingPlants(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_plant = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'sourcing_plants'


class Topographies(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_topo = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'topographies'


class TypeDocFoncier(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_type_doc_foncier = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'type_doc_foncier'


class Users(models.Model):
    uuid_user = models.UUIDField(unique=True)
    operateur_id = models.TextField(blank=True, null=True)
    c_com = models.ForeignKey(Communes, models.DO_NOTHING, db_column='c_com', to_field='c_com', blank=True, null=True)
    nom = models.TextField()
    prenom = models.TextField(blank=True, null=True)
    email = models.TextField(unique=True)
    mot_de_passe = models.TextField()
    num_tel = models.TextField(unique=True, blank=True, null=True)
    annee_naissance = models.IntegerField(blank=True, null=True)
    genre = models.TextField()  # This field type is a guess.
    adresse = models.TextField(blank=True, null=True)
    role = models.TextField()  # This field type is a guess.
    photo = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'users'


class UtilisationArbres(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_utilisation_arbre = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'utilisation_arbres'


class UtilisationSolBosquets(models.Model):
    nom = models.TextField()
    nom_malagasy = models.TextField(blank=True, null=True)
    uuid_sol_use = models.UUIDField(unique=True)

    class Meta:
        managed = False
        db_table = 'utilisation_sol_bosquets'
