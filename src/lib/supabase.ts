import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://vgdtduurqedgkytmtucq.supabase.co'
const supabasePublishableKey = 'sb_publishable_2b0A3E4HqHkfocKC1ZZ3ug_p9YG29op'

export const supabase = createClient(supabaseUrl, supabasePublishableKey)
