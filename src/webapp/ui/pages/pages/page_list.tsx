import { Result } from "neverthrow";
import React from "react";
import {
  Box,
  Button,
  Heading,
  Icon,
  Stack,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { Draft, PartialDraft } from "../../../casualcms/domain/model";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppConfig, useConfig } from "../../../config";

import { useAuth } from "../login/hooks";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { AddIcon, ArrowRightIcon, EditIcon, ViewIcon } from "@chakra-ui/icons";
import { Loader } from "../../components/loader";
import { ApiErrorUI } from "../../components/error_api";
import { PageBreadcrumb } from "../../components/breadcrumb";
import { PageDeletePopoverForm } from "./page_delete";

type PageRowProps = {
  page: PartialDraft;
};

type PageListTableProps = {
  parentPath: string | null;
  config: AppConfig;
  token: string;
  curPage: Draft | null;
};

export const PageRow: React.FunctionComponent<PageRowProps> = (
  props: PageRowProps
) => {
  const page = props.page;
  return (
    <Tr>
      <Td>
        <Link
          to={`/admin/pages/edit?${new URLSearchParams({
            page: page.metadata.path,
          })}`}
        >
          {page.slug}
        </Link>
      </Td>
      <Td>{page.title}</Td>
      <Td>{page.metadata.title}</Td>
      <Td>
        <Link
          to={`/admin/pages/edit?${new URLSearchParams({
            page: page.metadata.path,
          })}`}
        >
          <Icon as={EditIcon} marginEnd={2} />
          Edit
        </Link>
      </Td>
      <Td>
        <a
          href={`/admin/pages/preview?${new URLSearchParams({
            page: page.metadata.path,
          })}`}
          target="preview"
        >
          <Icon as={ViewIcon} marginEnd={2} />
          Preview
        </a>
      </Td>
      <Td>
        <Link
          to={`/admin/pages/?${new URLSearchParams({
            parent: page.metadata.path,
          })}`}
          data-testid="View child pages"
        >
          <Icon as={ArrowRightIcon} marginEnd={2} />
        </Link>
      </Td>
    </Tr>
  );
};

type PageListButtonsProps = {
  curPage: Draft | null;
  subPages: PartialDraft[];
};

export const PageListButtons: React.FunctionComponent<PageListButtonsProps> = (
  props: PageListButtonsProps
) => {
  const { curPage, subPages } = props;
  let navigate = useNavigate();
  const qsEdit = curPage
    ? new URLSearchParams({
        page: curPage.metadata.path,
      })
    : "";
  const qs = curPage
    ? new URLSearchParams({
        parent: curPage.metadata.path,
        type: curPage.metadata.type,
      })
    : "";
  return (
    <Stack p={4} spacing={4} direction="row" align="right">
      {qsEdit && (
        <Button
          onClick={() =>
            navigate(`/admin/pages/edit?${qsEdit}`, { replace: true })
          }
          colorScheme="cyan"
          leftIcon={<EditIcon />}
        >
          Edit
        </Button>
      )}

      <Button
        onClick={() => navigate(`/admin/pages/new?${qs}`, { replace: true })}
        colorScheme="cyan"
        leftIcon={<AddIcon />}
      >
        Add new page
      </Button>

      {curPage && subPages.length === 0 && (
        <PageDeletePopoverForm curPage={curPage} />
      )}
    </Stack>
  );
};

export const PageListTable: React.FunctionComponent<PageListTableProps> = (
  props: PageListTableProps
) => {
  const { config, parentPath, token } = props;
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [subPages, setSubPages] = React.useState<PartialDraft[]>([]);
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadSubPages() {
      let pages: Result<PartialDraft[], ApiError>;
      pages = await config.api.page.listDrafts(token, parentPath);
      pages
        .map((pages: PartialDraft[]) => setSubPages(pages))
        .mapErr((err: ApiError) => setError(err)); // FIXME
      setIsLoading(false);
    }
    loadSubPages();
    return function cleanup() {};
  }, [parentPath]);

  if (isLoading) {
    return <Loader label="Loading pages list" />;
  }
  if (error) {
    return <ApiErrorUI error={error} />;
  }
  return (
    <>
      <TableContainer>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Slug</Th>
              <Th>Title</Th>
              <Th>Type</Th>
              <Th>Edit</Th>
              <Th>View</Th>
              <Th>Childs</Th>
            </Tr>
          </Thead>
          <Tbody>
            {subPages.map((page, i) => (
              <PageRow page={page} key={i} />
            ))}
          </Tbody>
        </Table>
      </TableContainer>
      <PageListButtons curPage={props.curPage} subPages={subPages} />
    </>
  );
};

export const PageList: React.FunctionComponent<{}> = () => {
  // console.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
  // console.log("# Rendering page list")

  const config = useConfig();
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";

  const [curPage, setCurPage] = React.useState<Draft | null>(null);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [params, setParams] = useSearchParams();
  const parentPath = params.get("parent");

  React.useEffect(() => {
    async function loadCurPage() {
      let page: Result<Draft, ApiError>;
      if (parentPath) {
        page = await config.api.page.showDraft(token, parentPath);
        page
          .map((page: Draft) => setCurPage(page))
          .mapErr((err: ApiError) => setError(err));
      }
      setIsLoading(false);
    }
    if (token) {
      loadCurPage();
    }
    return () => {
      setCurPage(null);
      setError(null);
      setIsLoading(true);
    };
  }, [auth, parentPath]);

  if (isLoading) {
    return <Loader label="Loading pages" />;
  }
  return (
    <Box minW="1440px">
      {curPage && <Heading>{curPage.title}</Heading>}
      <PageBreadcrumb page={curPage} />
      <Box maxW="1440px">
        <ApiErrorUI error={error} />
        <PageListTable
          config={config}
          token={token}
          parentPath={parentPath}
          curPage={curPage}
        />
      </Box>
    </Box>
  );
};
