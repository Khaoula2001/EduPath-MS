# src/transformers/aggregator.py
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def aggregate_student_vle(student_vle: pd.DataFrame, courses: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate clicks per student-module-presentation
    """
    if student_vle.empty:
        logger.warning("student_vle empty -> returning empty df")
        return pd.DataFrame(columns=[
            'id_student','code_module','code_presentation','total_clicks','avg_clicks_per_activity',
            'activity_count','click_std','first_activity_day','last_activity_day','active_days',
            'engagement_intensity','days_without_activity','regularity_index','module_presentation_length','late_start_days'
        ])
    df = student_vle.copy()
    # ensure required columns exist
    for c in ['id_student','code_module','code_presentation','sum_click','date']:
        if c not in df.columns:
            df[c] = np.nan
    group = df.groupby(['id_student','code_module','code_presentation'])
    agg = group.agg(
        total_clicks=('sum_click','sum'),
        avg_clicks_per_activity=('sum_click','mean'),
        activity_count=('sum_click','count'),
        click_std=('sum_click','std'),
        first_activity_day=('date','min'),
        last_activity_day=('date','max'),
        active_days=('date','nunique')
    ).reset_index()
    agg['engagement_intensity'] = agg['total_clicks'] / agg['active_days'].replace(0,1)
    agg['days_without_activity'] = (agg['last_activity_day'] - agg['first_activity_day']) - agg['active_days']
    agg['regularity_index'] = agg['click_std'].fillna(0)
    # module length
    if {'code_module','code_presentation','module_presentation_length'}.issubset(courses.columns):
        agg = agg.merge(courses[['code_module','code_presentation','module_presentation_length']],
                        on=['code_module','code_presentation'], how='left')
    else:
        agg['module_presentation_length'] = np.nan
    agg['late_start_days'] = np.maximum(agg['first_activity_day'] - 1, 0).fillna(0).astype(int)
    logger.info("aggregate_student_vle -> %s rows", len(agg))
    return agg

def aggregate_student_assessments(student_assess: pd.DataFrame, assessments: pd.DataFrame) -> pd.DataFrame:
    """
    Compute mean score, std, submissions count per student-module-presentation
    """
    if student_assess.empty:
        return pd.DataFrame(columns=['id_student','code_module','code_presentation','mean_score','score_std','assessment_submissions_count','latest_assessment_score'])
    sa = student_assess.copy()
    # try to have code_module/presentation in sa; if not, try to join assessments
    if {'code_module','code_presentation'}.issubset(sa.columns) is False and 'id_assessment' in sa.columns and not assessments.empty:
        sa = sa.merge(assessments, on='id_assessment', how='left', suffixes=('','_meta'))
    # ensure grouping keys
    for c in ['id_student','code_module','code_presentation', 'score']:
        if c not in sa.columns:
            sa[c] = np.nan
    grp = sa.groupby(['id_student','code_module','code_presentation'])
    agg = grp.agg(
        mean_score=('score','mean'),
        score_std=('score','std'),
        assessment_submissions_count=('score','count'),
        latest_assessment_score=('score','last')
    ).reset_index()
    agg.fillna({'mean_score':0,'score_std':0,'assessment_submissions_count':0}, inplace=True)
    logger.info("aggregate_student_assessments -> %s rows", len(agg))
    return agg

def build_student_profiler(student_vle, student_assessment, registration, courses):
    vle_agg = aggregate_student_vle(student_vle, courses)
    assess_agg = aggregate_student_assessments(student_assessment, pd.DataFrame())
    if vle_agg.empty and assess_agg.empty:
        return pd.DataFrame()
    df = vle_agg.merge(assess_agg, on=['id_student','code_module','code_presentation'], how='left')
    if {'id_student','code_module','code_presentation','date_registration','date_unregistration'}.issubset(registration.columns):
        reg = registration[['id_student','code_module','code_presentation','date_registration','date_unregistration']].copy()
        df = df.merge(reg, on=['id_student','code_module','code_presentation'], how='left')
        df['study_duration'] = df['date_unregistration'] - df['date_registration']
        df['unregistered'] = df['date_unregistration'].notnull().astype(int)
    else:
        df['study_duration'] = np.nan
        df['unregistered'] = 0
    df['progress_rate'] = df['active_days'] / df['module_presentation_length'].replace(0,1)
    df['dropout_risk_signal'] = ((df['unregistered']==1).astype(int) + (df['study_duration']<0).astype(int)).fillna(0)
    df['engagement_drop_rate'] = 0.0  # placeholder
    logger.info("build_student_profiler -> %s rows", len(df))
    return df

def build_pathpredictor_features(student_vle, student_assessment, student_info):
    """
    Basic cumulative + simple rolling placeholders.
    For production replace placeholders by actual windowed rolling computations.
    """
    if student_vle.empty:
        return pd.DataFrame()
    daily = student_vle.groupby(['id_student','code_module','code_presentation','date']).agg(sum_click=('sum_click','sum')).reset_index()
    cum = daily.groupby(['id_student','code_module','code_presentation']).agg(
        cum_clicks=('sum_click','sum'),
        cum_active_days=('date','nunique')
    ).reset_index()
    cum['clicks_rolling_mean_7d'] = cum['cum_clicks'] / 7.0
    if not student_assessment.empty:
        assess = student_assessment.groupby(['id_student','code_module','code_presentation']).agg(
            cum_submissions_count=('id_assessment','count'),
            cum_weighted_score=('score','mean')
        ).reset_index()
    else:
        assess = pd.DataFrame(columns=['id_student','code_module','code_presentation','cum_submissions_count','cum_weighted_score'])
    out = cum.merge(assess, on=['id_student','code_module','code_presentation'], how='left').fillna(0)
    if not student_info.empty:
        hist = student_info.groupby('id_student').agg(historical_pass_rate_student=('final_result', lambda s: (s=='Pass').mean() if len(s)>0 else 0)).reset_index()
        out = out.merge(hist, on='id_student', how='left').fillna(0)
    logger.info("build_pathpredictor_features -> %s rows", len(out))
    return out
