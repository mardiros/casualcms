import React from "react";
import {
  Box,
  Button,
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
import { PartialSnippet } from "../../../casualcms/domain/model";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppConfig, useConfig } from "../../../config";

import { useAuth } from "../login/hooks";
import { Link, useNavigate } from "react-router-dom";
import { AddIcon, EditIcon } from "@chakra-ui/icons";
import { Result } from "neverthrow";
import { Loader } from "../../components/loader";
import { ApiErrorUI } from "../../components/error_api";
import { SnippetBreadcrumb } from "../../components/breadcrumb";

type SnippetRowProps = {
  snippet: PartialSnippet;
};

type SnippetListTableProps = {
  config: AppConfig;
  token: string;
};

export const SnippetRow: React.FunctionComponent<SnippetRowProps> = (
  props: SnippetRowProps
) => {
  const snippet = props.snippet;
  return (
    <Tr>
      <Td>
        <Link
          to={`/admin/snippets/edit/${snippet.metadata.type}/${snippet.key}`}
        >
          {snippet.key}
        </Link>
      </Td>
      <Td>{snippet.metadata.title}</Td>
      <Td>
        <Link
          to={`/admin/snippets/edit/${snippet.metadata.type}/${snippet.key}`}
        >
          <Icon as={EditIcon} marginEnd={2} />
          Edit
        </Link>
      </Td>
    </Tr>
  );
};

export const SnippetListTable: React.FunctionComponent<
  SnippetListTableProps
> = (props: SnippetListTableProps) => {
  const { config, token } = props;
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [snippets, setSnippets] = React.useState<PartialSnippet[]>([]);
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadSubSites() {
      let snippets: Result<PartialSnippet[], ApiError>;
      snippets = await config.api.snippet.listSnippets(token);
      snippets
        .map((snippets: PartialSnippet[]) => setSnippets(snippets))
        .mapErr((err: ApiError) => setError(err)); // FIXME
      setIsLoading(false);
    }
    if (token) {
      loadSubSites();
    }
    return function cleanup() {};
  }, []);

  if (isLoading) {
    return <Loader label="Loading snippet list" />;
  }
  if (error) {
    return <ApiErrorUI error={error} />;
  }
  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Slug</Th>
            <Th>Type</Th>
            <Th>Edit</Th>
          </Tr>
        </Thead>
        <Tbody>
          {snippets.map((snippet, i) => (
            <SnippetRow snippet={snippet} key={i} />
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

type SnippetListButtonsProps = {};
export const SnippetListButtons: React.FunctionComponent<
  SnippetListButtonsProps
> = (props: SnippetListButtonsProps) => {
  let navigate = useNavigate();
  return (
    <Stack p={4} spacing={4} direction="row" align="right">
      <Button
        colorScheme="cyan"
        onClick={() => navigate(`/admin/snippets/new`, { replace: true })}
        leftIcon={<AddIcon />}
      >
        Add new snippet
      </Button>
    </Stack>
  );
};

export const SnippetList: React.FunctionComponent<{}> = () => {
  const config = useConfig();
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";

  return (
    <Box minW="1440px">
      <SnippetBreadcrumb />
      <Box maxW="1440px">
        <SnippetListTable config={config} token={token} />
        <SnippetListButtons />
      </Box>
    </Box>
  );
};
