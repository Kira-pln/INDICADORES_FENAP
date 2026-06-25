import plotly.express as px
def bar(df,x,y,title,color=None):
    fig=px.bar(df,x=x,y=y,title=title,color=color,text_auto=True); fig.update_layout(height=380); return fig
def line(df,x,y,title,color=None):
    fig=px.line(df,x=x,y=y,title=title,color=color,markers=True); fig.update_layout(height=380); return fig
