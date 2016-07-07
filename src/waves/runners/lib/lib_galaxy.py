# -*-coding:Utf-8 -*
import time

from bioblend.galaxy import GalaxyInstance


class SBWGalaxyInstance(GalaxyInstance):
    """
    Custom Galaxy instance operator
    """

    def __init__(self, url, key=None, email=None, password=None):
        super(SBWGalaxyInstance, self).__init__(url, key, email, password)
        self.galaxy_server_path = ''
        self.galaxy_folder = ''
        self.roles = ''

    def set_galaxy_server_path(self, path):
        self.galaxy_server_path = path

    def get_galaxy_server_path(self):
        return self.galaxy_server_path

    def display_folders(self, library_id, project):
        """
        Retourne le contenu du dossier du projet situe dans le reperoire Synbiowatch de Galaxy "
        Args:
            library_id:
            project:

        Returns:

        """

        folders = self.libraries.show_library(library_id=library_id, contents=True)
        project_folder = []

        for data in folders:
            if (self.galaxy_folder + '/' + project) in data['name']:
                project_folder.append(data)

        return project_folder

    def display_histories(self, project):

        folders = self.histories.get_histories()
        project_folder = []

        for f in folders:
            if (self.galaxy_folder + '/' + project) in f['name']:
                project_folder.append(f)

        return project_folder

    @staticmethod
    def get_folder_by_path(folders, folder_path):
        # take a list of folder return galaxy folder id or '' if not found
        for f in folders:
            if f['name'] == folder_path:
                return f

    def create_folder(self, library_id, folder_path, folders=None):
        """
            Crée les dossiers dans le reperoire Synbiowatch de Galaxy
            a l'aide d'un path et de l'id galaxy de la librairie à utiliser.

        Args:
            folders:
            folder_path:
            library_id:
        """

        # TODO a optimiser
        # on recupere tout les fichiers de l'utilisateur de galaxy
        if not folders:
            folders = self.libraries.show_library(library_id=library_id, contents=True)

        # on recupere l'id du repertoire parent
        parent_folder_path, folder_name = folder_path.rsplit('/', 1)

        if not parent_folder_path:
            root_path = "/"
            parent_folder = self.get_folder_by_path(folders, root_path)

        else:
            parent_folder = self.get_folder_by_path(folders, parent_folder_path)


        # si le parent n'exite pas et si le parent n'est pas la racine
        if not parent_folder:
            parent_folder = self.create_folder(library_id, parent_folder_path, folders)

        payload = {
                   'name' : folder_name,
                   'folder_id':parent_folder['id'] ,
                   'create_type' : 'folder',
                   'roles': self.roles,
                   }
        newfolder = self.libraries._post(payload, id=library_id, contents=True)

        return newfolder[0]

    def get_or_create_dataset(self, project, library_id):
        """
        Retourne le contenu du dossier du projet situe dans le reperoire Synbiowatch de Galaxy
        crée le repertoire dans galaxy s'il n'exite pas
        """
        project_folders = self.display_folders(library_id, project)

        if project_folders:
            return project_folders

        else:
            path = '/' + self.galaxy_folder + '/' + project
            self.create_folder(library_id, path)

            # mise a jour
            project_folders = self.display_folders(library_id, project)
            return project_folders

    def import_file_to_galaxy(self, library_id, folder_id, project):
        """ Import file into galaxy in the library folder from link/'user'/"SynBioWatch"/project name
            Return list of imported files
        """
        server_dir = self.get_galaxy_server_path() + '/' + self.galaxy_folder + '/' + project + '/'
        return self.libraries.upload_file_from_server(library_id, server_dir, folder_id=folder_id, roles=self.roles)

    def import_dataset_to_history(self, project, library_id, dataset_id, suffix=""):

        # TODO rajouter des filtres
        # test si l'historique deja cree
        if suffix:
            suffix = '_' + suffix

        history_list = self.histories.get_histories(name=project + '_' + time.strftime("%d-%m-%Y") + suffix)

        if history_list:
            ghistory = history_list[0]
        else:
            ghistory = self.histories.create_history(project + '_' + time.strftime("%d-%m-%Y") + suffix)

        history_id = ghistory['id']


        # self.histories.create_history_tag(history_id, 'SBW')
        # self.histories.update_history(history_id,annotation="sbw")

        for selectedfile in dataset_id:

            payload = {'from_ld_id':selectedfile , 'content': selectedfile, 'source': 'library', 'roles':self.roles}

            # self.histories.upload_dataset_from_library(library_id, lib_dataset_id ) "not implemented with roles attribut"
            self.histories._post(payload, id=history_id, contents=True)

        return history_id

