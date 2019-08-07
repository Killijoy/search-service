searchd
{
    listen            = 9312
    listen            = 9306:mysql41

    log               = %(log_dir)s/searchd.log
    query_log         = %(log_dir)s/query.log

    read_timeout      = 5
    client_timeout    = 300

    workers           = threads # for RT to work
    dist_threads      = 4 # num of work threads
    binlog_path       = # disable logging

    pid_file          = /var/run/searchd.pid
}

indexer
{
    mem_limit = 256M
}

#
# * Sources
#
source base
{
    type                = mysql
    sql_host            = %(sql_host)s
    sql_port            = %(sql_port)s    # optional, default is 3306
    sql_user            = %(sql_user)s
    sql_pass            = %(sql_pass)s
    sql_db              = %(sql_db)s

    sql_query_pre       = SET NAMES utf8

    sql_attr_uint       = feed_id
    sql_attr_uint       = category_id
    sql_attr_timestamp  = post_date_ts
    sql_attr_string     = region
}

source main : base
{

    sql_query_range         = SELECT MIN(id), MAX(id) FROM api_post
    sql_query               = \
        SELECT p.id, p.feed_id, f.category_id, f.region, p.title, c.content, p.post_date_ts \
        FROM api_post p \
            JOIN api_feed f ON p.feed_id=f.id \
            LEFT JOIN api_postcontent c ON c.post_id=p.id \
        WHERE p.id BETWEEN $start AND $end

    sql_query_post_index    = REPLACE INTO search_indexlog (id, last_post_id, last_index_ts, index_name) \
                              VALUES (1, $maxid, UNIX_TIMESTAMP(), 'main')

    sql_range_step          = 100000
    sql_ranged_throttle     = 1000
}

source delta : base
{
    sql_query               = \
        SELECT p.id, p.feed_id, f.category_id, f.region, p.title, c.content, p.post_date_ts \
        FROM api_post p \
            JOIN api_feed f ON p.feed_id=f.id \
            LEFT JOIN api_postcontent c ON c.post_id=p.id \
        WHERE p.id > (SELECT MAX(last_post_id) FROM search_indexlog)

    sql_query_post_index    = REPLACE INTO search_indexlog (id, last_post_id, last_index_ts, index_name) \
                              VALUES (2, $maxid, UNIX_TIMESTAMP(), 'delta')

    # sql_query_killlist = \
    #     SELECT id \
    #     FROM api_post \
    #     WHERE post_date_ts > (SELECT MAX(last_index_ts) FROM search_indexlog WHERE index_name='main')
}

#
# * Indexes
#
index main
{
    source              = main
    path                = /usr/local/var/lib/sphinxsearch/posts.main

    morphology         = stem_enru
    min_stemming_len   = 3
    min_word_len       = 3
    expand_keywords    = 1
    html_strip         = 1
}

index delta : main
{
    source          = delta
    path            = /usr/local/var/lib/sphinxsearch/posts.delta
}

index posts
{
    type    = distributed
    local   = delta
    local   = main
}

# не будем использовать realtime-индекс
# index main_rt : main
# {
#     type                = rt
#     path                = /usr/local/var/lib/sphinxsearch/posts.rt
#     rt_mem_limit        = 1024M
#
#     rt_attr_uint        = feed_id
#     rt_attr_uint        = category_id
#     rt_attr_timestamp   = post_date_ts
#     rt_attr_string      = title
#     rt_attr_string      = content
#
#     rt_field            = title
#     rt_field            = content
# }