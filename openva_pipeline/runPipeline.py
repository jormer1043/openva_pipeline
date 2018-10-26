#------------------------------------------------------------------------------#
#    Copyright (C) 2018  Jason Thomas
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------#

import sys
from pipeline import Pipeline
from transferDB import PipelineError
from transferDB import DatabaseConnectionError
from transferDB import PipelineConfigurationError
from transferDB import ODKConfigurationError
from transferDB import OpenVAConfigurationError
from transferDB import DHISConfigurationError
from odk import ODKError
from openVA import OpenVAError
from openVA import SmartVAError
from dhis import DHISError

def runPipeline(database_file_name,
                database_directory,
                database_key,
                export_to_DHIS = True):
    """Runs through all steps of the OpenVA Pipeline.

    :param database_file_name: File name for the Transfer Database.
    :param database_directory: Path of the Transfer Database.
    :param datatbase_key: Encryption key for the Transfer Database
    :param export_to_DHIS: Indicator for posting VA records to a DHIS2 server.
    :type export_to_DHIS: (Boolean)
    """

    pl = Pipeline(dbFileName = database_file_name,
                  dbDirectory = database_directory,
                  dbKey = database_key,
                  useDHIS = export_to_DHIS)
    try:
        settings = pl.config()
    except PipelineConfigurationError as e:
        pl.logEvent(str(e), "Error")
        sys.exit(1)

    settingsPipeline = settings["pipeline"]
    settingsODK = settings["odk"]
    settingsOpenVA = settings["openVA"]
    settingsDHIS = settings["dhis"]

    try:
        odkBC = pl.runODK(settingsODK,
                          settingsPipeline)
        pl.logEvent("Briefcase Export Completed Successfully", "Event")
    except ODKError as e:
        pl.logEvent(str(e), "Error")
        sys.exit(1)

    try:
        rOut = pl.runOpenVA(settingsOpenVA,
                            settingsPipeline,
                            settingsODK.odkID,
                            pl.pipelineRunDate)
        pl.logEvent("OpenVA Analysis Completed Successfully", "Event")
    except (OpenVAError, SmartVAError) as e:
        pl.logEvent(str(e), "Error")
        sys.exit(1)

    if (export_to_DHIS):
        try:
            pipelineDHIS = pl.runDHIS(settingsDHIS,
                                      settingsPipeline)
            pl.logEvent("Posted Events to DHIS2 Successfully", "Event")
        except DHISError as e:
            pl.logEvent(str(e), "Error")
            sys.exit(1)

    try:
        pl.storeResultsDB()
        pl.logEvent("Stored Records to Xfer Database Successfully", "Event")
    except (PipelineError, DatabaseConnectionError, 
            PipelineConfigurationError) as e:
        pl.logEvent(str(e), "Error")
        sys.exit(1)

    try:
        pl.closePipeline()
        pl.logEvent("Successfully Completed Run of Pipeline", "Event")
    except (DatabaseConnectionError, DatabaseConnectionError) as e:
        pl.logEvent(str(e), "Error")
        sys.exit(1)

# if __name__ == "__main__":
#     runPipeline(database_file_name= "run_Pipeline.db", 
#                 database_directory = "tests",
#                 database_key = "enilepiP")