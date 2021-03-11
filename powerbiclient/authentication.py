#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft.

"""
Authenticates a Power BI User and acquires an access token
"""

import json
import msal

# NOTE: The client id used below is for "Microsoft Azure Cross-platform Command Line Interface" AAD app and a well known that already exists for all Azure services.
#       Refer blog: https://docs.microsoft.com/en-us/samples/azure-samples/data-lake-analytics-python-auth-options/authenticating-your-python-application-against-azure-active-directory/
DEFAULT_CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"

# Using Power BI default permissions
DEFAULT_SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]

# Power BI permissions for creating report
CREATE_REPORT_SCOPES = ["https://analysis.windows.net/powerbi/api/Dataset.ReadWrite.All", "https://analysis.windows.net/powerbi/api/Content.Create", "https://analysis.windows.net/powerbi/api/Workspace.ReadWrite.All"]

class AuthenticationResult:

    # Methods
    def __init__(self, client_id, scopes, access_token_result):
        """Create an instance of Authentication

        Args:
            client_id (string): your app has a client_id after you register it on AAD
            scopes (list[string]): scopes required to access Power BI API
            access_token_result (dict): authentication result

        Returns:
            object: Authentication object
        """
        self._access_token_result = access_token_result
        self._client_id = client_id
        self._scopes = scopes

    def get_access_token(self):
        """Returns the access token

        Returns:
            string: access token
        """

        return self._access_token_result.get('access_token')

    def get_access_token_details(self):
        """Returns the authentication result with access token

        Returns:
            dict: authentication result
        """

        return self._access_token_result

    def refresh_token(self):
        """Acquire token(s) based on a refresh token obtained from authentication result
        """
        app = msal.PublicClientApplication(self._client_id)
        token_result = app.acquire_token_by_refresh_token(self._access_token_result.get('refresh_token'), self._scopes)
        if "access_token" not in token_result:
            raise RuntimeError(token_result.get('error_description'))
        self._access_token_result = token_result


class DeviceCodeLoginAuthentication(AuthenticationResult):

    # Methods
    def __init__(self, client_id=None, scopes=None):
        """Initiate a Device Flow Auth instance

        Args:
            client_id (string): your app has a client_id after you register it on AAD
            scopes (list[string]): scopes required to access Power BI API

        Returns:
            object: Device Flow object
        """
        if not client_id:
            client_id = DEFAULT_CLIENT_ID
        self.client_id = client_id

        if not scopes:
            scopes = DEFAULT_SCOPES
        self.scopes = scopes
        auth_result = self._acquire_token_device_code()
        super().__init__(client_id, scopes, auth_result)

    def _acquire_token_device_code(self):
        """Returns the authentication result captured using device flow

        Returns:
            dict: authentication result
        """
        app = msal.PublicClientApplication(self.client_id)
        flow = app.initiate_device_flow(self.scopes)

        if "user_code" not in flow:
            raise ValueError("Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

        # Display the device code
        print("Performing interactive authentication. Please follow the instructions on the terminal.\n", flow["message"])

        # Ideally you should wait here, in order to save some unnecessary polling
        result = app.acquire_token_by_device_flow(flow)
        # By default it will block
        # You can follow this instruction to shorten the block time
        #    https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_by_device_flow
        # or you may even turn off the blocking behavior,
        # and then keep calling acquire_token_by_device_flow(flow) in your own customized loop.

        if "access_token" in result:
            print("You have logged in.\nInteractive authentication successfully completed.")
            return result
        else:
            raise RuntimeError(result.get("error_description"))


class InteractiveLoginAuthentication(AuthenticationResult):

    # Methods
    def __init__(self, client_id=None, scopes=None):
        """Acquire token interactively i.e. via a local browser

        Args:
            client_id (string): your app has a client_id after you register it on AAD
            scopes (list[string]): scopes required to access Power BI API

        Returns:
            object: Interactive authentication object
        """
        if not client_id:
            client_id = DEFAULT_CLIENT_ID
        self.client_id = client_id

        if not scopes:
            scopes = DEFAULT_SCOPES
        self.scopes = scopes
        auth_result = self._acquire_token_interactive()
        super().__init__(client_id, scopes, auth_result)

    def _acquire_token_interactive(self):
        """Returns the authentication result captured using interactive login

        Returns:
            dict: authentication result
        """
        app = msal.PublicClientApplication(self.client_id)
        print("A local browser window will be open for interactive sign in.")
        result = app.acquire_token_interactive(self.scopes)

        if "access_token" in result:
            print("You have logged in.\nInteractive authentication successfully completed.")
            return result
        else:
            raise RuntimeError(result.get("error_description"))
