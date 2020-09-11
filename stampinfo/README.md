

# UAS Stamp Info

## Purpose
This addon creates a frame around the rendered images and writes scene information on it.
It is a flexible alternative to the Metadata post processing integrated system of Blender.

## Installation:
The addon must be installed in Administrator mode so that the Pillow Python library can
be downloaded and deployed correctly.


## Features


- Can stamp a specified logo.
	Logo path can be relative to the path of the current blender file. It must then start with //

- Support also intergrated Blender Metadata (= text is moved if metadata are used)

[History](./CHANGELOG.md)

## Dev notes:
  * To do:
       - callback de restoration       -- intégrée à la fin du script RRS?
       - delete the temp file
       - mieux gérer les paths relatifs et messages de chemin invalide

       - restaurer les prefs précédentes
       - clean compo nodes (only them!!)
       - prémultipier les images PIL!!!

       - Stocker Last Rendered Frame pour pouvoir cleaner en cas de cancel et single rendered frame
       - garder les infos dans la scene

       - mettre les nodes compo à la fin du graph

       - faire un compo premult correct

## Possible future improvements:
       - Add hair cross, safe frame
       - Display metadata labels
       - Compositing nodes could be put in a separated scene to avoid breaking any existing compositing graph


## Principle:
   - At Prerender Init time:
       - creation of the postprocess nodes
           - we detect if there is a Composite note (expected to be the standard output)
               - if yes: we plug our graph on it with a mix
               - if not: we create our own graph
           - The resulting image has:
               - a large image at the stamp info res fully transparent
               - the stamped info
               - a RGB that is the rendered image below the stamped info




   - At Pre render Frame:
       - Voir si on peut rendre les frames de cadrage à ce moment là seulement

   - At Completed or Cancel:
       - cleaning of the nodes
       - the handlers stay in place


## Dev notes:
   - Handlers are NOT persistent
   - Compositing nodes are removed at the end of the process
   - Temp files used for the information are deleted at the next frame
   - Temp files are created in the render directory



## Resources:
   - Renderer:     https://docs.blender.org/api/current/bpy.ops.render.html?highlight=render#module-bpy.ops.render
   - handlers:     https://docs.blender.org/api/current/bpy.app.handlers.html
   - Compo nodes:  https://docs.blender.org/api/current/bpy.types.CompositorNodeImage.html
