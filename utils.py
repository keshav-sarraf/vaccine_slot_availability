def get_filtered_dists(search_query, dist_codes):
    search_query = search_query.lower()

    if search_query:
        filtered_dists = list(filter(lambda x: search_query in x['dist_name'].lower()
                                               or search_query in x['state_name'].lower()
                                     , dist_codes))
    else:
        filtered_dists = dist_codes
    return filtered_dists
