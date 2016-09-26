"""
WAVES services metas constants
------------------------------
"""
from __future__ import unicode_literals

#: META for external website link
META_WEBSITE = 'website'
#: META for external documentation link
META_DOC = 'doc'
#: META for any download link
META_DOWNLOAD = 'download'
#: META for related paper view
META_PAPER = 'paper'
#: META for miscellaneous stuff
META_MISC = 'misc'
#: META to display 'cite our work'
META_CITE = 'cite'
#: META Service command line
META_CMD_LINE = 'cmd'
#: META link to user guide
META_USER_GUIDE = 'rtfm'
#: META features included in service
META_FEATURES = 'feat'

SERVICE_META = (
    (META_WEBSITE, 'Online resources'),
    (META_DOC, 'Documentation'),
    (META_DOWNLOAD, 'Downloads'),
    (META_FEATURES, 'Features'),
    (META_MISC, 'Miscellaneous'),
    (META_PAPER, 'Related Paper'),
    (META_CITE, 'Citation'),
    (META_USER_GUIDE, 'User Guide'),
    (META_CMD_LINE, 'Command line')
)
