import MySQLdb
import numpy as np


def get_ghi(start_date, end_date):
    """
    Gets global horizontal irradiance values between the input dates

    :param start_date: datetime for the starting date
    :type start_date: datetime.datetime
    :param end_date: datetime for the ending date
    :type end_date: datetime.datetime
    :return: array of irradiance values every second
    :rtype: np.ndarray
    """
    db = MySQLdb.connect(host='lumos.el.nist.gov', port=3307, user='db_robot_select',
                         passwd='vdv', db='vistavision_db')
    c = db.cursor()
    c.execute('SELECT 19_refcell1_wm2 FROM ws_1_analogtable_0037 '
              'WHERE time_stamp BETWEEN \'{}\' '
              'and \'{}\''.format(start_date.strftime('%Y-%m-%d %H-%M-%S'),
                                  end_date.strftime('%Y-%m-%d %H-%M-%S')))
    out = c.fetchall()
    return np.array([float(n[0]) for n in out])

