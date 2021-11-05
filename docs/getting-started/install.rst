Installation
============

Supported versions
------------------

Stamp Info is developed and actively tested on Windows 10. Community users reported successful usage on Linux platform. 

stamp Info loads successfully and should work on 2.83 LTS up to 2.93.


.. _download:

Download
--------

Open the `latest release <https://github.com/ubisoft/stampinfo/releases/latest>`__  page from the Stamp Info Gihub `releases page <https://github.com/ubisoft/stampinfo/releases>`_.
Download the zip file listed in **Assets** that has the package icon: |package-icon|_.

.. |package-icon| image:: /img/package-icon.png
.. _package-icon: https://github.com/ubisoft/stampinfo/releases/latest

.. _installing:

Install of Stamp Info
---------------------

.. note::
    Stamp Info needs to download some external Python dependencies in order to be fully functionnal. Hence,
    when launching the installation of this add-on, be sure to match these conditions:

        - **Be connected to the internet**
        - **Be sure the firewall is not blocking the requests (use OpenVPN or equivalent if needed)**
        - In the case Blender has been installed from the executable installer package to your OS **launch Blender in Administrator mode**
        - Then inside Blender install the add-on as usual

Note that if you are using a verion of Blender coming for a zip file - which is probably the case when working in a studio and the
application was deployed by the production - the Administrator rights should not be required.

Inside Blender
**************

Once in Blender open the **Preferences** panel and go to the **Add-ons** section.
Press the **Install** button located at the top of the panel. A dialog box opens, pick the add-on
zip file you previously downloaded and validate.
The add-on header will be displayed in the Preferences panel. **Click on the checkbox at the left side of its name** to proceed to the installation.

Once the addon is enabled, a Stamp Info tab is displayed in the 3D viewport N-Panel.

**If you have any trouble during the installation process check the Troubleshooting FAQ** :ref:`Installation Error <error-during-installation>`


Install of complementary add-ons
--------------------------------

Stamp Info can work as is. Nevertheless we've developed 2 additional add-ons that are considerably 
expanding the features and capabilities of this tool. It is strongly advised to install them too
to get the full experience.

    - Download Ubisoft Shot Manager here: `Shot Manager latest release <https://github.com/ubisoft/shotmanager/releases/latest>`_
    - Download Ubisoft Video Tracks here: `Video Tracks latest release <https://github.com/ubisoft/videotracks/releases/latest>`_
