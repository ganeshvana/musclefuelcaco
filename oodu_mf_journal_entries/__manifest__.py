# -*- coding: utf-8 -*-
#################################################################################
# Author      : Dynexcel (<https://dynexcel.com/>)
# Copyright(c): 2015-Present dynexcel.com
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
  "name"                 :  "Print Journal Entries",
  "summary"              :  "This module will Add Print Option in Journal Entries",
  "category"             :  "Accounting",
  "version"              :  "13.0.1.0",
  "author"               :  "Oodu Implementers Pvt Ltd",
  "website"              :  "http://www.odooimplementers.com",
  "description"          :  """
This App will Add Print Option in Journal Entries
""",
  "live_test_url"        :  "",
  "depends"              :  [
                             'base','account',
                            ],
  "data"                 :  [
                             'views/journal_entries_report.xml',
                            ],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  
  # "images"		 :['static/description/banner.jpg'],
}
