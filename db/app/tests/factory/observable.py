from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional

from db import crud
from api_models.analysis_metadata import AnalysisMetadataCreate
from api_models.observable import ObservableCreate
from db.schemas.analysis import Analysis
from db.schemas.observable import Observable
from tests import factory


def create_or_read(
    type: str,
    value: str,
    parent_analysis: Analysis,
    db: Session,
    analysis_tags: Optional[list[str]] = None,
    context: Optional[str] = None,
    critical_points: Optional[str] = None,
    detection_points: Optional[str] = None,
    directives: Optional[list[str]] = None,
    display_type: Optional[str] = None,
    display_value: Optional[str] = None,
    expires_on: Optional[datetime] = None,
    for_detection: bool = False,
    history_username: Optional[str] = None,
    sort: Optional[int] = None,
    tags: Optional[list[str]] = None,
    time: Optional[datetime] = None,
    whitelisted: bool = False,
) -> Observable:
    factory.observable_type.create_or_read(value=type, db=db)

    metadata = []
    if analysis_tags is not None:
        for tag in analysis_tags:
            factory.metadata_tag.create_or_read(value=tag, db=db)
            metadata.append(AnalysisMetadataCreate(type="tag", value=tag))

    if critical_points is not None:
        for critical_point in critical_points:
            factory.metadata_critical_point.create_or_read(value=critical_point, db=db)
            metadata.append(AnalysisMetadataCreate(type="critical_point", value=critical_point))

    if detection_points is not None:
        for detection_point in detection_points:
            factory.metadata_detection_point.create_or_read(value=detection_point, db=db)
            metadata.append(AnalysisMetadataCreate(type="detection_point", value=detection_point))

    if directives is not None:
        for directive in directives:
            factory.metadata_directive.create_or_read(value=directive, db=db)
            metadata.append(AnalysisMetadataCreate(type="directive", value=directive))

    if display_type is not None:
        factory.metadata_display_type.create_or_read(value=display_type, db=db)
        metadata.append(AnalysisMetadataCreate(type="display_type", value=display_type))

    if display_value is not None:
        factory.metadata_display_value.create_or_read(value=display_value, db=db)
        metadata.append(AnalysisMetadataCreate(type="display_value", value=display_value))

    if sort is not None:
        factory.metadata_sort.create_or_read(value=sort, db=db)
        metadata.append(AnalysisMetadataCreate(type="sort", value=sort))

    if tags is not None:
        for tag in tags:
            factory.metadata_tag.create_or_read(value=tag, db=db)

    if time is not None:
        factory.metadata_time.create_or_read(value=time, db=db)
        metadata.append(AnalysisMetadataCreate(type="time", value=time))

    obj = crud.observable.create_or_read(
        model=ObservableCreate(
            analysis_metadata=metadata,
            context=context,
            expires_on=expires_on,
            for_detection=for_detection,
            history_username=history_username,
            tags=tags or [],
            type=type,
            value=value,
            whitelisted=whitelisted,
        ),
        parent_analysis=parent_analysis,
        db=db,
    )

    # Add the observable to its parent analysis
    parent_analysis.child_observables.append(obj)

    db.commit()

    return obj
