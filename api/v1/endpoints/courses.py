from typing import List

from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.course import Course
from schemas.course import CourseSchema
from core.deps import get_session

router = APIRouter()

@router.post('/', status_code=status.HTTP_201_CREATED, response_model = CourseSchema)
async def post_course(course: CourseSchema, db: AsyncSession = Depends(get_session)):
    new_course = Course(title = course.title, classes = course.classes, hours = course.hours)

    db.add(new_course)
    await db.commit()

    return new_course


@router.get('/', response_model = List[CourseSchema])
async def get_course(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(Course)
        result = await session.execute(query)
        courses: List[Course] = result.scalars().all()

    return courses

@router.get('/{course_id}', response_model = CourseSchema, status_code = status.HTTP_200_OK)
async def get_course(course_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select (Course).filter(Course.id == course_id)
        result = await session.execute(query)
        course = result.scalar_one_or_none()
    if course:
        return course
    raise HTTPException(detail = 'Course not found', status_code = status.HTTP_404_NOT_FOUND)

@router.put('/{course_id}', response_model = CourseSchema, status_code = status.HTTP_202_ACCEPTED)
async def put_course(course_id: int, course: CourseSchema, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(Course).filter(Course.id == course_id)
        result = await session.execute(query)
        course_up = result.scalar_one_or_none()

        if course_up:
            course_up.title = course.title
            course_up.classes = course.classes
            course_up.hours = course.hours

            await session.commit()

            return course_up
        else:
            raise HTTPException(detail='Curso não encontrado.',
                                status_code=status.HTTP_404_NOT_FOUND)



@router.delete('/{course_id}', status_code = status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select (Course).filter(Course.id == course_id)
        result = await session.execute(query)
        course_del = result.scalar_one_or_none()
    if course_del:
        await session.delete(course_del)
        await session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(detail = 'Course not found', status_code = status.HTTP_404_NOT_FOUND)