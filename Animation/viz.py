import datetime

#INPUT START AND END DATE/TIME
#FOR DATE/TIME USED SINGLE DIGIT FOR SINGLE NUMBER (i.e 4 NOT 04)
start_date='1948:1:1' #'yyyy:m:d' 
end_date='2021:2:28'
start_time='0:0:0' #'h:m:s'
end_time='0:0:0'

#PARSING INPUT DATE/TIME
date_time=[start_date,start_time,end_date,end_time]
dt_dict={}
key=0
for i in date_time:
    a=i.split(':')
    for j in range(len(a)):
        key +=1
        dt_dict[key]=int(a[j])


# These functions are part of https://github.com/GispoCoding/qgis_plugin_tools/blob/master/tools/raster_layers.py

def set_raster_renderer_to_singleband(layer: QgsRasterLayer, band: int = 1) -> None:
    """
    Set raster renderer to singleband
    :param layer: raster layer
    """
    # https://gis.stackexchange.com/a/377631/123927 and https://gis.stackexchange.com/a/157573/123927
    provider: QgsRasterDataProvider = layer.dataProvider()
    renderer: QgsSingleBandGrayRenderer = QgsSingleBandGrayRenderer(layer.dataProvider(), band)

    stats: QgsRasterBandStats = provider.bandStatistics(band, QgsRasterBandStats.All, layer.extent(), 0)
    min_val = max(stats.minimumValue, 0)
    max_val = max(stats.maximumValue, 0)

    enhancement = QgsContrastEnhancement(renderer.dataType(band))
    contrast_enhancement = QgsContrastEnhancement.StretchToMinimumMaximum
    enhancement.setContrastEnhancementAlgorithm(contrast_enhancement, True)
    enhancement.setMinimumValue(min_val)
    enhancement.setMaximumValue(max_val)
    layer.setRenderer(renderer)
    layer.renderer().setContrastEnhancement(enhancement)
    layer.triggerRepaint()
    
def set_band_based_on_range(layer: QgsRasterLayer, t_range: QgsDateTimeRange) -> int:
    """

    :param layer: raster layer
    :param t_range: temporal range
    :return: band number
    """
    band_num = 1
    tprops: QgsRasterLayerTemporalProperties = layer.temporalProperties()
    if tprops.isVisibleInTemporalRange(t_range) and t_range.begin().isValid() and t_range.end().isValid():
        if tprops.mode() == QgsRasterLayerTemporalProperties.ModeFixedTemporalRange:
            layer_t_range: QgsDateTimeRange = tprops.fixedTemporalRange()
            start: datetime.datetime = layer_t_range.begin().toPyDateTime()
            end: datetime.datetime = layer_t_range.end().toPyDateTime()
            delta = (end - start) / layer.bandCount()
            band_num = int((t_range.begin().toPyDateTime() - start) / delta) + 1
            set_raster_renderer_to_singleband(layer, band_num)
    return band_num
    
def set_fixed_temporal_range(layer: QgsRasterLayer, t_range: QgsDateTimeRange) -> None:
    """
    Set fixed temporal range for raster layer
    :param layer: raster layer
    :param t_range: fixed temporal range
    """
    mode = QgsRasterLayerTemporalProperties.ModeFixedTemporalRange
    tprops: QgsRasterLayerTemporalProperties = layer.temporalProperties()
    tprops.setMode(mode)
    if t_range.begin().timeSpec() == 0 or t_range.end().timeSpec() == 0:
        begin = t_range.begin()
        end = t_range.end()
        begin.setTimeSpec(Qt.TimeSpec(1))
        end.setTimeSpec(Qt.TimeSpec(1))
        t_range = QgsDateTimeRange(begin, end)
    tprops.setFixedTemporalRange(t_range)
    tprops.setIsActive(True)
    
def temporal_range_changed(t_range: QgsDateTimeRange):
    layer = iface.activeLayer()
    if isinstance(layer, QgsRasterLayer):
        set_band_based_on_range(layer, t_range)
    
def set_range():
    mode = QgsRasterLayerTemporalProperties.ModeFixedTemporalRange
    
temporal_controller: QgsTemporalController = iface.mapCanvas().temporalController()
temporal_controller.updateTemporalRange.connect(temporal_range_changed)
# Add one second to make the last frame visible
set_fixed_temporal_range(iface.activeLayer(), QgsDateTimeRange(datetime.datetime(dt_dict[1], dt_dict[2], dt_dict[3], dt_dict[4], dt_dict[5],dt_dict[6]), datetime.datetime(dt_dict[7], dt_dict[8], dt_dict[9], dt_dict[10], dt_dict[11], dt_dict[12])))