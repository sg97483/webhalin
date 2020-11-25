def get_sql(now_date, logger, is_park_test, testPark):
    valid_lots = [
        '16239', '18904', '18901', '12868', '18913', '15683', '18937', '18936', '15313', '45674', '11558', '18970',
        '18956', '16175', '16184', '20863', '15437', '16001', '18969', '18972', '18973', '18971', '18964', '15740',
        '12845', '12936', '12903', '18996', '18997', '12313', '11367', '19004', '12951', '18995', '4588', '18991',
        '70004', '70005', '70006', '19030', '19029', '19031', '16170', '19028', '19038', '12872', '19020', '19017',
        '19010', '19044', '18967', '12750', '19047', '16105', '15619', '19048', '19056', '19063', '19061', '2810',
        '16209', '19066', '19064', '19065', '19070', '19071', '19077', '19078', '19081', '19080', '28864', '15644',
        '18930', '11349', '16210', '19084', '19082', '13825', '16360', '19087', '19083', '45655', '12806', '19040',
        '15591', '19000', '12997', '11917', '12124', '12184', '13007', '19091', '15008', '19043', '15160', '16003',
        '19090', '18577', '16173', '22982', '19086', '12904', '16215', '19085', '18981', '18999', '12817', '19101',
        '19111', '19112', '14506', '14994', '12130', '19089', '12050', '19119', '70008', '70009', '70010', '19120',
        '19121', '18966', '18957', '15309', '12532', '12749', '19116', '19124', '19125', '12929', '19128', '35546',
        '19126', '14541', '19110', '19131', '19100', '16096', '12539', '45009', '12183', '19136', '18963', '18959',
        '19138', '19151',
        '11290', '15639', '19155', '18968', '45304', '19166', '19168', '14618', '19172', '19170', '19171', '18958',
        '19173', '19174',
        '19139', '19140', '19141', '19142', '19143', '19145', '19146', '19147', '19148', '19149', '19156', '19157',
        '19158', '19162',
        '19160',
        '19180', '19183', '19181', '19182', '19188', '19189', '19190',
        '19198',
        '12766',
        '19073', '19194', '19197', '19193',
        '19208', '19203', '19191', '19235',
        '19230', '14588', '19202', '19022', '19159', '19234',
        '19215', '19241', '19196', '19248', '19247',
        '19219', '19218', '19212', '19267', '19250', '19240', '19239', '19161', '19272', '19271',
        '19199', '19206', '19258',
        # 여기서부터 나이스파크
        '19280', '19281', '19282', '19283', '19284', '19285', '19286', '19287', '19288', '19289', '19290',
        '19291', '19292', '19293', '19294', '19295', '19296', '19297', '19298', '19299', '19300',
        '19301', '19302', '19303', '19304', '19305', '19306', '19307', '19308', '19309', '19310',
        '19311', '19312', '19330',
        # 나이스 신규현장 끝
        '19238', '19210', '19226', '19321', '19276', '19195', '19325', '19273',
        '19331', '19236', '19209', '16434', '19334', '19324', '19364', '19328',
        '19336', '18945', '45304', '19266', '19329'
    ]

    str_lots = ", ".join(valid_lots)
    parking_lot_range = "(" + str_lots + ")"

    logger.info("today is : " + now_date + "\n")
    sql = "SELECT id, parkId, agCarNumber, totalTicketType FROM T_PAYMENT_HISTORY WHERE " \
          "parkId IN " + parking_lot_range + " " \
          "AND cancelledYN IS NULL " \
          "AND (inCarCheck = 'N' OR actualInDtm IS NOT NULL) " \
          "AND reservedStDtm LIKE '" + now_date + "%' " \
          "AND TotalTicketType NOT LIKE '월주차%' " \
          "AND TotalTicketType NOT LIKE '월연장%' " \
          "AND TotalTicketType NOT LIKE '%자동결제%' " \
          "AND actualOutDtm IS NULL " \
          "AND agHp = 0 "

    if is_park_test:
        sql += "AND parkId IN ('" + str(testPark) + "') "

    sql += "ORDER BY actualInDtm DESC, parkId DESC;"
    # "ORDER BY actualInDtm ASC, parkId ASC;"
    # "ORDER BY actualInDtm DESC, parkId DESC;"
    # "AND parkId IN ('" + str(testPark) + "') " \
    return sql