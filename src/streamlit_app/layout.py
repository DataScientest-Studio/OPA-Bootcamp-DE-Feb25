import requests
from API.api_calls import get_current_prices


def add_coin_images(st):
    """
    Adds coin images to the Streamlit app.
    """
    cols = st.columns([0.5, 2, 0.5, 0.5, 2, 0.5, 0.5, 2, 0.5])

    with cols[1]:
        st.image("Images/BTC.jpg", use_container_width=True)
        st.markdown(
            """<p style=" font-family: 'Georgia', serif;font-size: 18px;font-style: italic;font-weight: bold;color: gold;text-align: center; margin-top: 10px;">✨ Bitcoin ✨</p>""",
            unsafe_allow_html=True
        )
        #st.caption("Bitcoin (BTC)")

    with cols[4]:
        st.image("Images/PEP.jpg", use_container_width=True)
        st.markdown(
            """<p style=" font-family: 'Georgia', serif;font-size: 18px;font-style: italic;font-weight: bold;color: silver;text-align: center; margin-top: 10px;">✨ Pepecoin ✨</p>""",
            unsafe_allow_html=True
        )
        #st.caption("Pepecoin (PEP)")

    with cols[7]:
        st.image("Images/XRP.jpg", use_container_width=True)
        st.markdown(
            """<p style=" font-family: 'Georgia', serif;font-size: 18px;font-style: italic;font-weight: bold;color: #8c7853;text-align: center; margin-top: 10px;">✨ Ripple ✨</p>""",
            unsafe_allow_html=True
        )
        #st.caption("XRP Ripple")
    
    #get current prices placeholders
    btc_price, pep_price, xrp_price = get_current_prices()
    priceCols = st.columns([0.5, 2, 0.5, 0.5, 2, 0.5, 0.5, 2, 0.5])
    with priceCols[1]:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.metric(label="BTC/USDT", value=f"${btc_price:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with priceCols[4]:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.metric("PEP/USDT: ", f"${pep_price:.7f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with priceCols[7]:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.metric("XRP/USDT: ", f"${xrp_price:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
   
# Map intensity to colors (volume chart)
def volume_color(row):
    alpha = 0.4 + 0.6 * row['VolumeColorIntensity']
    if row['close_price'] >= row['open_price']:
        return f'rgba(0, 200, 0, {alpha:.2f})'  # green shades
    else:
        return f'rgba(200, 0, 0, {alpha:.2f})'  # red shades


